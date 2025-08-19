-- General table to hold metric type
DROP TABLE IF EXISTS metric_type;
CREATE TABLE metric_type (
    ID SERIAL PRIMARY KEY,
    name VARCHAR,
    units VARCHAR
);
CREATE INDEX metric_type_name ON metric_type(name);

INSERT INTO metric_type (name, units) VALUES ('SWE', 'mm');

-- Information on model run
DROP TABLE IF EXISTS isnobal_version;
CREATE TABLE isnobal_version (
    ID SERIAL PRIMARY KEY,
    description VARCHAR
);

-- iSnobal Zonal SWE
DROP TABLE IF EXISTS isnobal_zonal_swe;
CREATE TABLE isnobal_zonal_swe (
    ID SERIAL PRIMARY KEY,
    Value FLOAT,
    datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metric_type_id INT NOT NULL,
    isnobal_version_id INT NOT NULL,
    cbrfc_zone_id INT NOT NULL,
    FOREIGN KEY (metric_type_id) REFERENCES metric_type(ID) ON DELETE CASCADE,
    FOREIGN KEY (isnobal_version_id) REFERENCES isnobal_version(ID) ON DELETE CASCADE,
    FOREIGN KEY (cbrfc_zone_id) REFERENCES cbrfc_zones(GID) ON DELETE CASCADE
);
CREATE INDEX isnobal_zonal_swe_datetime ON isnobal_zonal_swe(datetime);
CREATE INDEX isnobal_zonal_swe_metric ON isnobal_zonal_swe(metric_type_id);
CREATE INDEX isnobal_version_zonal_swe ON isnobal_zonal_swe(isnobal_version_id);
CREATE INDEX isnobal_zonal_swe_cbrfc_zone ON isnobal_zonal_swe(cbrfc_zone_id);
