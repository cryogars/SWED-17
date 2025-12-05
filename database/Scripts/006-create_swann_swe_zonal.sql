DROP TABLE IF EXISTS swann_zonal_swe;

CREATE TABLE public.swann_zonal_swe (
    z_date date NOT NULL,
    cbrfc_zone_id int4 NOT NULL,
    swe numeric NOT NULL,
    CONSTRAINT swann_zonal_swe_pkey PRIMARY KEY (cbrfc_zone_id, z_date),
    CONSTRAINT swann_zonal_swe_cbrfc_zone_id_fkey FOREIGN KEY (cbrfc_zone_id) REFERENCES public.cbrfc_zones(gid)
);
