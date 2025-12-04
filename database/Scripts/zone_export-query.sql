SELECT ST_AsGDALRaster(ST_Union(zone_mask.rast), 'GTiff')
FROM zone_mask_as_raster('ALEC2HUF') AS zone_mask;


SELECT ST_ENVELOPE(zone_mask.rast) 
FROM zone_mask_as_raster('ALEC2HUF') AS zone_mask;
