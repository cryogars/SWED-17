-- Update records
UPDATE cu_boulder 
    SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD')
    WHERE swe_date is NULL;

VACUUM FULL cu_boulder;
