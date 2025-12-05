ALTER TABLE __tablename__
    ADD swe_date date;

CREATE INDEX ON __tablename__(swe_date);
