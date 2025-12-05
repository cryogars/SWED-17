-- Update records and populate date based of imported file name
UPDATE aso
    SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD')
    WHERE swe_date IS NULL;

VACUUM FULL aso;
