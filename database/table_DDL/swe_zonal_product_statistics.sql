-- University of Arizona Zonal SWE
DROP TABLE IF EXISTS ua_zonal_swe;
CREATE TABLE ua_zonal_swe (
    datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    Value FLOAT,
    metric_type_id INT NOT NULL,
    cbrfc_zone_id INT NOT NULL,
    FOREIGN KEY (metric_type_id) REFERENCES metric_type(ID) ON DELETE CASCADE,
    FOREIGN KEY (cbrfc_zone_id) REFERENCES cbrfc_zones(GID) ON DELETE CASCADE,
    PRIMARY KEY(datetime, cbrfc_zone_id)
);

CREATE INDEX ua_zonal_swe_cbrfc_zone ON ua_zonal_swe
    USING btree (cbrfc_zone_id);
CREATE INDEX ua_zonal_swe_metric ON ua_zonal_swe
    USING btree (metric_type_id);

-- SNODAS Zonal SWE
DROP TABLE IF EXISTS snodas_zonal_swe;
CREATE TABLE snodas_zonal_swe (
    datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    Value FLOAT,
    metric_type_id INT NOT NULL,
    cbrfc_zone_id INT NOT NULL,
    FOREIGN KEY (metric_type_id) REFERENCES metric_type(ID) ON DELETE CASCADE,
    FOREIGN KEY (cbrfc_zone_id) REFERENCES cbrfc_zones(GID) ON DELETE CASCADE
    PRIMARY KEY(datetime, cbrfc_zone_id)
);

CREATE INDEX snodas_zonal_swe_cbrfc_zone ON snodas_zonal_swe
    USING btree (cbrfc_zone_id);
CREATE INDEX snodas_zonal_swe_metric ON snodas_zonal_swe
    USING btree (metric_type_id);

-- CU Boulder SWE
CREATE TABLE cu_boulder_zonal_swe (
    value float8 NULL,
    datetime timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metric_type_id int4 NOT NULL,
    cbrfc_zone_id int4 NOT NULL,
    CONSTRAINT cu_boulder_swe_primary_composite_key PRIMARY KEY (datetime, cbrfc_zone_id),
    CONSTRAINT cu_boulder_zonal_swe_cbrfc_zone_id_fkey FOREIGN KEY (cbrfc_zone_id) REFERENCES public.cbrfc_zones(gid) ON DELETE CASCADE,
    CONSTRAINT cu_boulder_zonal_swe_metric_type_id_fkey FOREIGN KEY (metric_type_id) REFERENCES public.metric_type(id) ON DELETE CASCADE
);

CREATE INDEX cu_boulder_zonal_swe_cbrfc_zone ON cu_boulder_zonal_swe
    USING btree (cbrfc_zone_id);
CREATE INDEX cu_boulder_zonal_swe_metric ON cu_boulder_zonal_swe
    USING btree (metric_type_id);

-- ASO Zonal SWE
CREATE TABLE aso_zonal_swe (
    value float8 NULL,
    datetime timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metric_type_id int4 NOT NULL,
    cbrfc_zone_id int4 NOT NULL,
    CONSTRAINT aso_swe_primary_composite_key PRIMARY KEY (datetime, cbrfc_zone_id),
    CONSTRAINT aso_zonal_swe_cbrfc_zone_id_fkey FOREIGN KEY (cbrfc_zone_id) REFERENCES public.cbrfc_zones(gid) ON DELETE CASCADE,
    CONSTRAINT aso_zonal_swe_metric_type_id_fkey FOREIGN KEY (metric_type_id) REFERENCES public.metric_type(id) ON DELETE CASCADE
);

CREATE INDEX aso_zonal_swe_cbrfc_zone ON aso_zonal_swe
    USING btree (cbrfc_zone_id);
CREATE INDEX aso_zonal_swe_metric ON aso_zonal_swe
    USING btree (metric_type_id);