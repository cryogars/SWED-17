import json

import dash_bootstrap_components as dbc
import dash_leaflet as dl
from nb_paths import SWE_DB

import dash

dash.register_page(__name__, path="/overview_map", name="Overview Map", order=3)

QUERY = """
SELECT basin_name, ST_AsGeoJSON(geometry) AS geometry_json FROM isnobal_domains;
"""

def load_polygons():
    with SWE_DB.query(QUERY) as results:
        rows = results.fetchall()

    polygons = []
    for name, geometry_json in rows:
        ring = json.loads(geometry_json)["coordinates"][0][0]
        positions = [[lat, lon] for lon, lat in ring]

        polygons.append(
            dl.Polygon(
                positions=positions,
                color="#d45b36",
                fillOpacity=0.18,
                children=dl.Popup(name),
            )
        )

    return polygons


layout = dbc.Container(
    dl.Map(
        [
            dl.TileLayer(
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            ),
            *load_polygons(),
        ],
        center=[38, -107],
        zoom=6,
        style={"width": "100%", "height": "78vh"},
    ),
    fluid=True,
)