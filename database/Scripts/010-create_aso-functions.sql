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
