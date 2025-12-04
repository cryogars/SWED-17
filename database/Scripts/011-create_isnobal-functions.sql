-- Function to average iSnobal SWE into an areal mean
-- iSnobal values are in meters
DROP FUNCTION IF EXISTS public.isnobal_areal_swe_for_date;
CREATE FUNCTION public.isnobal_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (isnobal_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round(avg(zone_data.swe)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('isnobal', zone_name, target_date) as zone_data
$function$
;