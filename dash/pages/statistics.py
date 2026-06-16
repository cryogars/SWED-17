import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from metrics import metric_table_data

import dash
from dash import html

dash.register_page(__name__, path="/statistics")

table_data = metric_table_data()
column_defs = [{"field": str(i)} for i in table_data.columns]
for col in column_defs:
    if col["field"] == "Zone Name":
        col["cellClass"] = {"function": "colorByZone(params)"}

zone_legend = [
    ("lower-zone", "Lower"),
    ("middle-zone", "Middle"),
    ("upper-zone", "Upper"),
    ("only-zone", "Single"),
]

layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            [
                html.Div(
                    [
                        html.Span(
                            "Zone colors:", className="zone-legend-title"
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            className=f"zone-swatch {cls}"
                                        ),
                                        html.Span(label),
                                    ],
                                    className="zone-legend-item",
                                )
                                for cls, label in zone_legend
                            ],
                            className="zone-legend-items",
                        ),
                    ],
                    className="zone-legend",
                ),
                dag.AgGrid(
                    id="db-table",
                    rowData=table_data.to_dict("records"),
                    columnDefs=column_defs,
                    columnSize="responsiveSizeToFit",
                    defaultColDef={
                        "sortable": True,
                        "filter": True,
                        "floatingFilter": True,
                        "resizable": True,
                        "flex": 1,
                    },
                    dashGridOptions={
                        "pagination": True,
                        "paginationPageSize": 100,
                    },
                    style={"height": "100%", "width": "100%"},
                ),
            ],
            style={"height": "90vh"},
        )
    ),
    fluid=True,
)
