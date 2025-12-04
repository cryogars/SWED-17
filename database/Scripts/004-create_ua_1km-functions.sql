-- Function to average UA SWE into an areal mean
-- UA SWE values are in mm
DROP FUNCTION IF EXISTS public.ua_1km_areal_swe_for_date;
CREATE FUNCTION public.ua_1km_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (ua_1km_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round(avg(zone_data.swe)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('ua_1km', zone_name, target_date) as zone_data
$function$
;
