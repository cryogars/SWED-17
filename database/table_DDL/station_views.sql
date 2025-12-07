-- Station Views
-- Table with station data and isnobal domains are created via Jupyter notebooks

-- View joining the isnobal domains and station locations
DROP VIEW public.stations_in_basin;
CREATE OR REPLACE VIEW public.stations_in_basin AS
SELECT
    snst.station_triplet,
    snst.station_name,
    snst.geometry,
    LOWER(isb.basin_name) AS basin_name
FROM
    public.snotel_sites AS snst
INNER JOIN
    public.isnobal_domains AS isb
ON
    ST_Within(
        snst.geometry,
        isb.geometry_4326
);
-- Index to query basin names independent on input casing
CREATE INDEX idx_isnobal_domains_basin_name_lower ON isnobal_domains (lower(basin_name));

-- Second geometry column on the isnobal domains for faster lookup of stations
-- iSnobal domains are in UTM and all station locations are stored in WGS84
ALTER TABLE public.isnobal_domains
    ADD COLUMN geometry_4326 GEOMETRY(Polygon, 4326);
UPDATE public.isnobal_domains
    SET geometry_4326 = ST_Transform(geometry, 4326);