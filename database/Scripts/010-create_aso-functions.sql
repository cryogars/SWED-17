-- Function to average ASO SWE into an areal mean
-- ASO values are in meters
DROP FUNCTION IF EXISTS public.aso_areal_swe_for_date;
CREATE FUNCTION public.aso_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (aso_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round((avg(zone_data.swe) * 1000)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('aso', zone_name, target_date) as zone_data
$function$
;

-- Find SWE values for given station.
-- Transforms the station location to the native SRID of the dataset
DROP FUNCTION IF EXISTS public.aso_swe_at_station;
CREATE OR REPLACE FUNCTION public.aso_swe_at_station(target_station_name text)
RETURNS TABLE(swe_date date, raw_pixel_value double precision) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        WITH transformed_sites AS (
            SELECT
                ST_Transform(ss.geometry, ST_SRID(r.rast)) AS target_geom
            FROM
                snotel_sites AS ss,
                aso_swe_13n AS r
            WHERE
                ss.station_name = %L
            LIMIT 1
        )
        SELECT
            swe_raster.swe_date,
            ST_Value(
                swe_raster.rast,
                ts.target_geom
            ) AS raw_pixel_value
        FROM
            aso_swe_13n AS swe_raster
        JOIN
            transformed_sites AS ts ON  swe_raster.rast && ts.target_geom;
    ',
        target_station_name
    );
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS public.aso_depth_at_station;
CREATE OR REPLACE FUNCTION public.aso_depth_at_station(target_station_name text)
RETURNS TABLE(swe_date date, raw_pixel_value double precision) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        WITH transformed_sites AS (
            SELECT
                ST_Transform(ss.geometry, ST_SRID(r.rast)) AS target_geom
            FROM
                snotel_sites AS ss,
                aso_depth_13n AS r
            WHERE
                ss.station_name = %L
            LIMIT 1
        )
        SELECT
            swe_raster.swe_date,
            ST_Value(
                swe_raster.rast,
                ts.target_geom
            ) AS raw_pixel_value
        FROM
            aso_depth_13n AS swe_raster
        JOIN
            transformed_sites AS ts ON swe_raster.rast & ts.target_geom;
    ',
        target_station_name
    );
END;
$$ LANGUAGE plpgsql;
