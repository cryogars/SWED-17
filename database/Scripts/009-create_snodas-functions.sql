-- Function to average SNODAS SWE into an areal mean
-- SNODAS values are in mm
DROP FUNCTION IF EXISTS public.snodas_areal_swe_for_date;
CREATE FUNCTION public.snodas_areal_swe_for_date(zone_name TEXT, target_date TEXT)
  RETURNS TABLE (snodas_swe real)
  LANGUAGE SQL
AS $function$
  SELECT round(avg(zone_data.swe)::numeric, 1)
  FROM public.swe_from_product_for_zone_and_date('snodas', zone_name, target_date) as zone_data
$function$
;
