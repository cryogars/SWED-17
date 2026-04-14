-- View to fetch SWE zonal SWE data across available tables

DROP VIEW IF EXISTS public.zonal_swe;
CREATE OR REPLACE VIEW public.zonal_swe
AS SELECT
    datetime AS date,
    COALESCE(isz.value, 0) AS isnobal_swe,
    COALESCE(ssz.value, 0) AS snodas_swe,
    COALESCE(uzs.value, 0) AS ua_swe,
    COALESCE(csz.value, 0) AS cu_boulder_swe,
    asz.value AS aso_swe,
    cbrfc_zone_id
FROM snodas_zonal_swe ssz
FULL JOIN (
    SELECT cbrfc_zone_id, datetime, value
    FROM isnobal_zonal_swe
    WHERE isnobal_version_id = 2
      AND EXTRACT(HOUR FROM datetime AT TIME ZONE 'UTC') = 0
) isz USING (cbrfc_zone_id, datetime)
FULL JOIN ua_zonal_swe         uzs USING (cbrfc_zone_id, datetime)
FULL JOIN cu_boulder_zonal_swe csz USING (cbrfc_zone_id, datetime)
FULL JOIN aso_zonal_swe        asz USING (cbrfc_zone_id, datetime)
LEFT JOIN cbrfc_zones          cz  ON cbrfc_zone_id = cz.gid;