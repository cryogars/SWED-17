-- Sample query to link imported iSnobal records with cbrfc zone
UPDATE isnobal 
SET ch5_id = subquery.id
FROM (
    SELECT id FROM cbrfc_ch5id WHERE ch5_id = 'ALEC2'
) as subquery
WHERE isnobal.filename like '%ALEC2%';
