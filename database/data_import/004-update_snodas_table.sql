-- Add date column and index
ALTER TABLE snodas ADD swe_date date;
CREATE INDEX ON snodas(swe_date);

-- Update current records
UPDATE snodas SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD'); 
VACUUM FULL snodas;
