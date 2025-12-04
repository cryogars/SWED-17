-- Create SWE date column and add index to it
ALTER TABLE nwm ADD swe_date date;
CREATE INDEX ON nwm(swe_date);

-- Add date column and index
UPDATE nwm 
    SET swe_date = to_date(split_part(filename, '_', 1), 'YYYYMMDD')
    WHERE swe_date is NULL;

VACUUM FULL nwm;
