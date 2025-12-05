-- Add date column and index
ALTER TABLE cu_boulder ADD swe_date date;
CREATE INDEX ON cu_boulder(swe_date);

-- Update current records
UPDATE cu_boulder SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD'); 
VACUUM FULL cu_boulder;