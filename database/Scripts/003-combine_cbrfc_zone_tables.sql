-- Create unique zone region associations
CREATE TYPE cbrfc_region AS enum ('UC', 'LC', 'GSL');

-- Use the LC table as the central going forward
ALTER TABLE CBRFC_ZONES_LC RENAME TO cbrfc_zones;
ALTER TABLE cbrfc_zones ADD COLUMN region cbrfc_region;

Update cbrfc_zones SET region = 'LC'; 

-- ADD UC entries
INSERT INTO cbrfc_zones (ch5_id, segment, zone, descriptio, fgid, area_mi, area_km, x_centroid, y_centroid, z50_ft, z50_m, zonenum, geom) 
SELECT ch5_id, segment, zone, descriptio, fgid, area_mi, area_km, x_centroid, y_centroid, z50_ft, z50_m, zonenum, geom
FROM cbrfc_zones_uc;

Update cbrfc_zones SET region = 'UC' WHERE region IS NULL; 

-- Add GSL entries
INSERT INTO cbrfc_zones (ch5_id, segment, zone, descriptio, fgid, area_mi, area_km, x_centroid, y_centroid, z50_ft, z50_m, zonenum, geom) 
SELECT ch5_id, segment, zone, descriptio, fgid, area_mi, area_km, x_centroid, y_centroid, z50_ft, z50_m, zonenum, geom
FROM cbrfc_zones_GSL;

Update cbrfc_zones SET region = 'GSL' WHERE region IS NULL; 

-- Require regions going forward
ALTER TABLE cbrfc_zones ALTER COLUMN region SET NOT NULL;

-- Clean up
DROP TABLE cbrfc_zones_uc;
DROP TABLE cbrfc_zones_gsl;

-- Improve search queries
CREATE INDEX zone_idx ON cbrfc_zones(zone);

-- Fix import column name
ALTER TABLE cbrfc_zones RENAME COLUMN descriptoi TO description;

-- Create table with Ch5 IDs to link with ASO tables
CREATE TABLE cbrfc_ch5id AS
SELECT ROW_NUMBER() OVER (ORDER BY ch5_id) AS ID, * FROM 
   (SELECT DISTINCT ch5_id FROM cbrfc_zones cz);

-- Add constraint and a description column to copy from the original
ALTER TABLE cbrfc_ch5id
    ADD description TEXT,
    ADD CONSTRAINT cbrfc_ch5id_pkey PRIMARY key(id);
CREATE UNIQUE INDEX cbrfc_ch5_id_idx ON cbrfc_ch5id(ch5_id);

-- Rename old column and add foreigh key constraint
ALTER TABLE cbrfc_zones RENAME ch5_id TO ch5_id_name;
ALTER TABLE cbrfc_zones 
    ADD ch5_id integer,
    ADD CONSTRAINT cbrfc_ch5id_fk FOREIGN KEY (ch5_id) REFERENCES cbrfc_ch5id(id);

-- Populate the new column
UPDATE cbrfc_zones
SET ch5_id=subquery.CCI_ID
FROM (
    SELECT cci.id AS CCI_ID, cci.ch5_id AS CH5_name, cz.ch5_id AS CZ_CH5_ID 
    FROM cbrfc_zones cz LEFT JOIN cbrfc_ch5id cci ON cz.ch5_id_name = cci.ch5_id
) AS subquery
WHERE ch5_id_name=subquery.CH5_name;

-- Populate descriptions
UPDATE cbrfc_ch5id 
    SET description=cbrfc_zones.description
    FROM cbrfc_zones 
    WHERE cbrfc_zones.ch5_id = cbrfc_ch5id.id;

-- Drop column that is now defined via foreign key, the descrption column,
-- and index to the latter
DROP INDEX ch5_id_idx IF EXISTS;
ALTER TABLE cbrfc_zones 
    DROP COLUMN ch5_id_name
    DROP COLUMN description;
CREATE INDEX cbrfc_zones_ch5_id_fk_idx ON cbrfc_zones(ch5_id);

-- Add not-null contraint to prevent orphans
ALTER TABLE cbrfc_zones ADD CONSTRAINT cbrfc_ch5id_fk_check CHECK(ch5_id IS NOT NULL);

-- Final table clean up
VACUUM FULL ANALYZE cbrfc_zones; 
