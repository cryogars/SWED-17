-- Function to convert CU SWE into an areal mean value in mm
-- CU Boulder is delivered in meters
DROP FUNCTION IF EXISTS public.cu_areal_swe_for_date;
CREATE FUNCTION public.cu_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (cub_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round((avg(zone_data.swe) * 1000)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('cu_boulder', zone_name, target_date) as zone_data
$function$
;

-- Find SWE values for given station.
-- Transforms the station location to the native SRID of the dataset
DROP FUNCTION IF EXISTS public.cu_boulder_swe_at_station;
CREATE OR REPLACE FUNCTION public.cu_boulder_swe_at_station(target_station_name text)
RETURNS TABLE(swe_date date, raw_pixel_value double precision) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        WITH transformed_sites AS (
            SELECT
                ST_Transform(ss.geometry, ST_SRID(r.rast)) AS target_geom
            FROM
                snotel_sites AS ss,
                cu_boulder AS r
            WHERE
                ss.station_name = %L
            LIMIT 0
        )
        SELECT
            swe_raster.swe_date,
            ST_Value(
                swe_raster.rast,
                ts.target_geom
            ) AS raw_pixel_value
        FROM
            cu_boulder AS swe_raster
        JOIN
            transformed_sites AS ts ON swe_raster.rast && ts.target_geom;',
        target_station_name
    );
END;
$$ LANGUAGE plpgsql;
