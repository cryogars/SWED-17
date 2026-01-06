-- CBRFC zone buffer function
-- Ensure that the perimeter of a zone is accounted for when extracting raster
-- based SWE with the ST_CLIP function
DROP FUNCTION public.cbrfc_zone_buffer;
CREATE OR REPLACE FUNCTION public.cbrfc_zone_buffer(zone_name TEXT)
  RETURNS TABLE(geom geometry, buffered_envelope geometry)
  LANGUAGE SQL
AS $function$
    WITH cbrfc_zone AS (
        select geom from cbrfc_zones czu where zone = zone_name
    )
    SELECT cbrfc_zone.geom, st_buffer(st_envelope(cbrfc_zone.geom), 0.05) AS buffered_geom
    FROM cbrfc_zone;
$function$;

-- Function to transform CBRFC zone to target SRID
-- Returns the zone geometry in product SRID and a buffered envelope for querying
-- Query steps:
--  1. Get SRID of target raster to clip from (raster_srid)
--  2. Get target CBRFC zone and transform to SRID from target raster
DROP FUNCTION IF EXISTS public.transform_zone;
CREATE OR REPLACE FUNCTION public.transform_zone(product TEXT, zone_name TEXT)
  RETURNS TABLE (geom geometry, transformed_envelope geometry)
  LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY EXECUTE FORMAT(
        'WITH zone_buffer as (
           SELECT * FROM cbrfc_zone_buffer($1)
        ),
        raster_srid AS (
            SELECT ST_SRID(%1$I.rast) AS epsg FROM %1$I ORDER BY %1$I.rid LIMIT 1
        )
        SELECT
            ST_TRANSFORM(cz.geom, raster_srid.epsg),
            ST_TRANSFORM(zb.buffered_envelope, raster_srid.epsg)
        FROM cbrfc_zones cz, raster_srid, zone_buffer zb
        WHERE cz.zone = $1',
        product
    ) USING zone_name;
END
$function$
;

-- Function to query a SWE product for given zone and date
-- Query steps:
--  1. Use transform_zone function to get SRID and buffered envelope (cbrfc_zone).
--  2. Get centroids for each raster pixel that falls within the CBRFC zone (product_pixels)
--  3. Get values for the pixels (final query)
DROP FUNCTION IF EXISTS public.swe_from_product_for_zone_and_date;
CREATE OR REPLACE FUNCTION public.swe_from_product_for_zone_and_date(product TEXT, zone_name TEXT, target_date TEXT)
 RETURNS TABLE(swe double precision, raster_center geometry)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY EXECUTE FORMAT(
        'WITH cbrfc_zone AS (
            SELECT * FROM transform_zone($1, $2)
        ),
        product_pixels AS (
            SELECT
                (ST_PixelAsCentroids(
                    ST_CLIP(r.rast, cz.geom, true)
                )
            ).*
            FROM %1$I AS r
            JOIN cbrfc_zone AS cz ON r.rast && cz.transformed_envelope
            WHERE r.swe_date = TO_DATE($3, ''YYYY-MM-DD'')
        )
        SELECT pp.val, pp.geom
        FROM product_pixels as pp',
        product
    ) USING product, zone_name, target_date;
END
$function$
;

-- Function to query a SWE product for given zone across all available dates
-- This will only return values when there is at least 95% coverage and the
-- SWE not null.
DROP FUNCTION IF EXISTS public.swe_from_product_for_zone;
CREATE OR REPLACE FUNCTION public.swe_from_product_for_zone(
    product text, zone_name text
)
RETURNS TABLE(swe_date date, swe double PRECISION, coverage double PRECISION)
LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY EXECUTE FORMAT(
        'WITH cbrfc_zone AS (
            SELECT geom, ST_AREA(geom) as zone_area
            FROM transform_zone($1, $2)
        ),
        tile_stats AS (
            SELECT (
              ST_SummaryStats(
                ST_Clip(r.rast, cz.geom, true)
              )
            ).* as stats,
            r.swe_date,
            ST_PixelWidth(r.rast) * ST_PixelHeight(r.rast) as pixel_size,
            cz.zone_area
            FROM %1$I AS r
            JOIN cbrfc_zone AS cz ON ST_INTERSECTs(r.rast, cz.geom)
        ),
        date_values AS (
          SELECT
            swe_date,
            -- Weighted average: (sum of values) / (count of pixels)
            SUM(stats.sum) / NULLIF(SUM(stats.count), 0) as swe,
            (SUM(stats.count) * AVG(pixel_size)) / AVG(zone_area) as coverage
          FROM tile_stats as stats
          GROUP BY stats.swe_date
        )
        SELECT *
        FROM date_values
        WHERE swe IS NOT NULL AND coverage > 0.95
        ORDER BY swe_date ASC
        ',
        product
    ) USING product, zone_name;
END
$function$
;

-- Function to query by zone returning all dates and associated geom. The
-- geom column wil combine all centroids to a multi-polygon. This function
-- is mostly helpful for debugging purposes.

DROP FUNCTION IF EXISTS public.swe_from_product_for_zone_with_geom;
CREATE OR REPLACE FUNCTION public.swe_from_product_for_zone_with_geom(
    product text, zone_name text
)
RETURNS TABLE(swe_date date, swe double PRECISION, geom geometry)
LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY EXECUTE FORMAT(
        'WITH cbrfc_zone AS (
            SELECT * FROM transform_zone($1, $2)
        ),
        product_pixels AS (
            SELECT
                (ST_PixelAsCentroids(
                    ST_CLIP(r.rast, cz.geom, true)
                )
            ).*,
            r.swe_date
            FROM %1$I AS r
            JOIN cbrfc_zone AS cz ON r.rast && cz.transformed_envelope
        )
        SELECT
          pp.swe_date,
          avg(pp.val) as SWE,
          ST_COLLECT(pp.geom)
        FROM product_pixels as pp
        GROUP BY pp.swe_date',
        product
    ) USING product, zone_name;
END
$function$
;
