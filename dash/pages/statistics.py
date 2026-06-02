from typing import Optional

import dash_bootstrap_components as dbc
from metrics import METRIC_OPTIONS, metric_bar_chart
from plotly.graph_objects import Figure
from ui_elements import zone_dropdown

import dash
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/statistics")

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "SWE Model Performance Metrics",
                    className="text-center my-4",
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    zone_dropdown(),
                    md=6,
                    xs=12,
                    className="mb-3",
                ),
                dbc.Col(
                    [
                        dbc.Label("Select Metric:"),
                        dbc.RadioItems(
                            id="metric-selector",
                            options=METRIC_OPTIONS,
                            value="net",
                            inline=True,
                        ),
                    ],
                    md=6,
                    xs=12,
                    className="mb-3",
                ),
            ]
        ),
        dbc.Row(dbc.Col(dcc.Graph(id="swe-metrics"), width=12)),
    ],
    fluid=True,
)

@callback(
    Output("swe-metrics", "figure"),
    Input("segment-dropdown", "value"),
    Input("metric-selector", "value"),
)
def update_graph(segment: Optional[str], metric: str) -> Figure | None:
    """
    Update the statistics figure with the selected segment and metric.

    Args:
        segment: Selected zone segment from the dropdown.
        metric: Metric column name to plot.

    Returns:
        Plotly Figure object or None if no segment is passed in.
    """
    if segment is None:
        return None

    return metric_bar_chart(segment, metric)
