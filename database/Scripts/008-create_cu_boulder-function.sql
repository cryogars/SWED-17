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
