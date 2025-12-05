-- Function to average National Water Model SWE into an areal mean
-- NWM values are in kg/m2, but stored as INT with a scale factor of 0.1
DROP FUNCTION IF EXISTS public.nwm_areal_swe_for_date;
CREATE FUNCTION public.nwm_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (nwm_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round(avg(zone_data.swe * 0.1)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('nwm', zone_name, target_date) as zone_data
$function$
;