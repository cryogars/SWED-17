-- Calculate percentage of cbrfc area within a SWE pixel
-- UA SWE example
CREATE OR REPLACE VIEW public.UA_ALEC2HLF_PERC AS (
    WITH cbrfc_zone AS (
        select geom, buffered_envelope from public.cbrfc_zone_buffer('ALEC2HLF')
    ),
    swann_pixels AS (
        SELECT
            (ST_PixelAsPolygons(
                ST_CLIP(
                    ssm.rast,
                    cbrfc_zone.buffered_envelope
                ),
                1,
                FALSE
            )).*
        FROM swann_swe_mask_4k ssm, cbrfc_zone
    )
    SELECT swann_pixels.val, swann_pixels.geom, 
        ST_Area(ST_Intersection(swann_pixels.geom, cbrfc_zone.geom))/ST_Area(swann_pixels.geom) AS overlap,
        ST_Area(swann_pixels.geom) AS pixel,
        ST_Area(cbrfc_zone.geom) AS zone_area
    FROM cbrfc_zone, swann_pixels
    WHERE ST_Intersects(swann_pixels.geom, cbrfc_zone.geom)
);
