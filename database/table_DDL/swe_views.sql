-- View to fetch SWE zonal SWE data across available tables

DROP VIEW IF EXISTS public.zonal_swe;
CREATE OR REPLACE VIEW public.zonal_swe
AS WITH swe_one AS (
         SELECT
            COALESCE(isz.cbrfc_zone_id, ssz.cbrfc_zone_id) AS cbrfc_zone_id,
            COALESCE(isz.datetime, ssz.datetime) AS date,
            isz.value AS isnobal_swe,
            ssz.value AS snodas_swe
           FROM isnobal_zonal_swe isz
             FULL JOIN snodas_zonal_swe ssz ON isz.cbrfc_zone_id = ssz.cbrfc_zone_id AND isz.datetime = ssz.datetime
          WHERE isz.isnobal_version_id = 2 AND EXTRACT(hour FROM isz.datetime) = 0::numeric
    ),
    swe_two AS (
         SELECT
            COALESCE(sv.cbrfc_zone_id, csz.cbrfc_zone_id) AS cbrfc_zone_id,
            COALESCE(sv.date, csz.datetime) AS date,
            sv.isnobal_swe,
            sv.snodas_swe,
            csz.value AS cu_boulder_swe
           FROM swe_one sv
             FULL JOIN cu_boulder_zonal_swe csz
                ON sv.cbrfc_zone_id = csz.cbrfc_zone_id AND sv.date = csz.datetime
    ),
    swe_three AS (
         SELECT
            COALESCE(sv.cbrfc_zone_id, asz.cbrfc_zone_id) AS cbrfc_zone_id,
            COALESCE(sv.date, asz.datetime) AS date,
            sv.isnobal_swe,
            sv.snodas_swe,
            sv.cu_boulder_swe,
            asz.value AS aso_swe
           FROM swe_two sv
             FULL JOIN aso_zonal_swe asz
                ON sv.cbrfc_zone_id = asz.cbrfc_zone_id AND sv.date = asz.datetime
    )
 SELECT
    sv.date,
    cz.zone AS zone_name,
    sv.isnobal_swe,
    sv.snodas_swe,
    uzs.value AS ua_swe,
    sv.cu_boulder_swe,
    sv.aso_swe,
    sv.cbrfc_zone_id
   FROM swe_three sv
     FULL JOIN ua_zonal_swe uzs ON sv.cbrfc_zone_id = uzs.cbrfc_zone_id AND sv.date = uzs.datetime
     LEFT JOIN cbrfc_zones cz ON COALESCE(sv.cbrfc_zone_id, uzs.cbrfc_zone_id) = cz.gid;
