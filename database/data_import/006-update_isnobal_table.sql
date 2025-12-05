-- Update table structure, add SWE date, and link with CBRFC zone
ALTER TABLE isnobal 
    ADD swe_date date,
    ADD ch5_id integer,
    ADD CONSTRAINT cbrfc_ch5id_fk FOREIGN KEY (ch5_id) REFERENCES cbrfc_ch5id(id);

UPDATE isnobal SET swe_date =  to_date(split_part(filename, '_', 1), 'YYYYMMDD');

CREATE INDEX ON isnobal(swe_date);
CREATE INDEX isnobal_ch5id_fk_idx ON isnobal(ch5_id);

VACUUM FULL isnobal;
