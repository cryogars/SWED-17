-- Function to extract UA SWE raster centroids that fall within a CBRFC zone
-- Uses the 4 km raster grid
DROP FUNCTION public.ua_4k_mask_for_zone;
CREATE OR REPLACE FUNCTION public.ua_4k_mask_for_zone(zone_name text)
 RETURNS TABLE(swe double precision, raster_center geometry)
 LANGUAGE sql
AS $function$
    WITH cbrfc_zone AS (
        select geom, buffered_envelope from public.cbrfc_zone_buffer(zone_name)
    ),
    swann_pixels AS (
        SELECT
            (ST_PixelAsCentroids(
                ST_CLIP(
                    ssm.rast,
                    cbrfc_zone.buffered_envelope,
                    true
                )
            )).*
        FROM swann_swe_mask_4k ssm, cbrfc_zone
        WHERE ST_Intersects(ssm.rast, cbrfc_zone.buffered_envelope)
    )
    SELECT swann_pixels.val, swann_pixels.geom
    FROM cbrfc_zone, swann_pixels
    WHERE ST_Within(swann_pixels.geom, cbrfc_zone.geom); 
$function$
;