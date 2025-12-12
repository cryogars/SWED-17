-- Station Views

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
        isb.geometry
);
