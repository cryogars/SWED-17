-- Create SWE date column and add index to it
ALTER TABLE ua_1km ADD swe_date date;
CREATE INDEX ON ua_1km(swe_date);

-- Add date column and index
UPDATE ua_1km 
    SET swe_date = to_date(split_part(filename, '_', 1), 'YYYYMMDD')
    WHERE swe_date is NULL;

VACUUM FULL ua_1km;
