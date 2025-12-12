CREATE OR REPLACE FUNCTION public.zone_mask_as_raster(zone_name text)
RETURNS TABLE (rast raster)
LANGUAGE SQL
AS $function$
    WITH reference_raster AS (
        SELECT rast FROM swann_swe_mask_4k ssm LIMIT 1
    )
    SELECT ST_AsRaster(
            ST_UNION(zone_mask.geom),
            reference_raster.rast,
            '8BUI',
            1,
            0
        )
    FROM mask_for_zone(zone_name) AS zone_mask, reference_raster
    GROUP BY reference_raster.rast;
$function$
;