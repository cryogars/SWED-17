-- Table to chache SWE dataset metrics
CREATE TABLE public.swe_metrics (
	cbrfc_id int8 NOT NULL,
	"year" int8 NOT NULL,
	"name" text NOT NULL,
	overlapping float8 NULL,
	timing_shift float8 NULL,
	magnitude float8 NULL,
	net int8 NULL,
	mae float8 NULL,
	CONSTRAINT swe_metrics_pkey PRIMARY KEY (cbrfc_id, year, name)
);
CREATE INDEX idx_cbrfc_id ON public.swe_metrics USING btree (cbrfc_id);
