-- Bounding Boxes for iSnobal domains
DROP TABLE IF EXISTS isnobal_domains;
CREATE TABLE public.isnobal_domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(MultiPolygon, 4326)
);
CREATE INDEX idx_isnobal_domains_name ON public.isnobal_domains
  USING BTREE (name);
CREATE INDEX idx_isnobal_domains_geom ON public.isnobal_domains
  USING GIST (geom);
  USING GIST (geometry);
CREATE INDEX idx_isnobal_domains_basin_name_lower ON public.isnobal_domains
  (lower(basin_name));

INSERT INTO isnobal_domains (basin_name, geometry)
VALUES (
  'SWCO', ST_Transform(ST_MakeEnvelope(183440.422, 4101063.000, 332140.406, 4257663.000, 32613), 4326)
),(
  'ERW_ext', ST_Transform(ST_MakeEnvelope(258772, 4273213, 393372, 4377013, 32613), 4326)
),(
'Colkrem', ST_Transform(ST_MakeEnvelope(346631.5, 4347007.5, 456631.5, 4492007.5, 32613), 4326)
),(
'Great_Basin', ST_Transform(ST_MakeEnvelope(399761.250, 4376741.000, 635961.250, 4592341.00, 32612), 4326)
),(
'Uppergreen', ST_Transform(ST_MakeEnvelope(507513.938, 4638563.000, 662613.938, 4821063.000, 32612), 4326)
),(
'Yampa', ST_Transform(ST_MakeEnvelope(270140.438, 4426191.500, 365340.438, 4530491.500, 32613), 4326)
);

-- Show all cbrfc zones within iSnobal model domains
DROP VIEW IF EXISTS public.cbrfc_zones_in_isnobal;
CREATE OR REPLACE VIEW public.cbrfc_zones_in_isnobal AS
SELECT
    cz.gid,
    cz.fgid,
    cz.segment,
    cz.ZONE,
    lower(isb.basin_name) AS basin_name
FROM
  cbrfc_zones cz
JOIN isnobal_domains isb ON
    st_within(cz.geom, ST_Transform(isb.geometry, ST_SRID(cz.geom)));
