UPDATE isnobal 
    SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD')
    WHERE swe_date IS NULL;

VACUUM FULL isnobal;
