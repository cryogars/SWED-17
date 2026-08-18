import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_mantine_components as dmc

import dash
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/isnobal", order=2, name="iSnobal")

EARTHMOVER_BASE_URL = (
    "https://compute.earthmover.io/v1/services/tiles/Cryogars/"
)
EARTHMOVER_TILE = (
    EARTHMOVER_BASE_URL + "{basin}/main/tiles/WebMercatorQuad/{{z}}/{{y}}/{{x}}"
    "?variables={variable}&colorscalerange={min},{max}&time={date}T23%3A00%3A00"
    "&style=raster%2FBlues&width=512&height=512&f=png&render_errors=false"
)
EARTHMOVER_LEGEND = (
    EARTHMOVER_BASE_URL + "{basin}/main/tiles/legend"
    "?variables={variable}&colorscalerange={min},{max}&style=raster%2FBlues"
    "&vertical=false"
)
COLOR_RANGE = {
    "thickness": [0, 3],
    "specific_mass": [0, 150],
    "SWI": [0, 100],
}

content = [
    dbc.Row(
        [
            dbc.NavbarBrand("iSnobal Spatial Viewer"),
            dbc.Col(
                [
                    html.Label("Select Area:", className="fw-bold mb-1"),
                    html.Div(
                        dcc.Dropdown(
                            id="area-selector",
                            options=[
                                {"label": "ERW", "value": "ERW-ext"},
                                {"label": "Colkrem", "value": "Colkrem"},
                                {
                                    "label": "Great Basin",
                                    "value": "Great-Basin",
                                },
                            ],
                            value="ERW-ext",
                            clearable=False,
                            className="mb-4 text-dark",
                        ),
                        style={"position": "relative", "zIndex": 1100},
                    ),
                ]
            ),
            dbc.Col(
                [
                    dmc.MantineProvider(
                        dmc.DatePickerInput(
                            id="date-picker",
                            label="Pick a date",
                            dropdownType="modal",
                            valueFormat="YYYY-MM-DD",
                            minDate="2020-10-01",
                            maxDate="2026-07-15",
                            w=250,
                            modalProps={"zIndex": 1200},
                        ),
                        theme={
                            "colorScheme": "light",
                        },
                    )
                ],
            ),
            dbc.Col(
                [
                    html.Label("Select Variable:", className="fw-bold mb-1"),
                    dcc.Dropdown(
                        id="variable-selector",
                        options=[
                            {"label": "Snow Depth", "value": "thickness"},
                            {
                                "label": "Snow Water Equivalent",
                                "value": "specific_mass",
                            },
                            {"label": "Surface Water Input", "value": "SWI"},
                        ],
                        value="thickness",
                        clearable=False,
                        className="mb-4 text-dark",
                        style={"zIndex": 1100},
                    ),
                ]
            ),
        ]
    ),
    dbc.Row(
        dbc.Col(
            dl.Map(
                [
                    dl.TileLayer(
                        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
                    ),
                    dl.TileLayer(
                        id="earthmover-tiles",
                        url="",
                        tileSize=512,
                        zoomOffset=-1,
                    ),
                ],
                center=[
                    38.9,
                    -106.9,
                ],
                zoom=9,
                style={"width": "100%", "height": "100%"},
            ),
            style={"height": "70vh", "width": "100%"},
        )
    ),
    dbc.Row(dbc.Col(html.Div(id="legend"))),
]

layout = dbc.Container(
    fluid=True,
    children=content,
)


@callback(
    Output("earthmover-tiles", "url"),
    [Input("area-selector", "value"), Input("date-picker", "value"), Input("variable-selector", "value")],
)
def update_tiles(basin, date, variable):
    if date is None:
        return

    min_val, max_val = COLOR_RANGE.get(variable, [0, 3])
    return EARTHMOVER_TILE.format(
        basin=basin, date=date, variable=variable, min=min_val, max=max_val
    )


@callback(
    Output("legend", "children"),
    [Input("area-selector", "value"), Input("variable-selector", "value")],
)
def update_legend(basin, variable):
    min_val, max_val = COLOR_RANGE.get(variable, [0, 3])
    legend_url = EARTHMOVER_LEGEND.format(
        basin=basin, variable=variable, min=min_val, max=max_val
    )
    return html.Img(src=legend_url, className="mx-auto d-block")
