-- Update table structure, add SWE date, and link with CBRFC zone
ALTER TABLE aso 
    ADD swe_date date,
    ADD ch5_id integer,
    ADD CONSTRAINT cbrfc_ch5id_fk FOREIGN KEY (ch5_id) REFERENCES cbrfc_ch5id(id);

UPDATE aso SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD');

CREATE INDEX ON aso(swe_date);
CREATE INDEX aso_ch5id_fk_idx ON aso(ch5_id);

VACUUM FULL aso;
