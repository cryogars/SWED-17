-- Sample update after importing data for ERW
UPDATE aso 
SET ch5_id = subquery.id
FROM (
    SELECT id FROM cbrfc_ch5id WHERE ch5_id = 'ALEC2'
) as subquery
WHERE aso.filename like '%ALEC%';
