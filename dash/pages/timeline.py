from typing import Optional

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from config import DATASETS
from data_load import load_and_group
from metrics import METRIC_OPTIONS, metric_bar_chart
from timeline_plot import add_scatter_line
from ui_elements import zone_dropdown

import dash
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path='/')

layout = dbc.Container(
    [
        dbc.Row([html.H3("Mean areal SWE")]),
        dbc.Row(
            [
                dbc.Col(
                    zone_dropdown(),
                    width=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Timeline", className="mt-4"),
                        html.Div(
                            dcc.Loading(
                                id="loading-animation",
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id="swe-figure",
                                        config={"responsive": True},
                                    )
                                ],
                            ),
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Row(
                    [
                        html.H3("SWE Comparison Metrics", className="mt-4"),
                        dcc.Markdown(
                            "Metrics are calculated relative to Snow-17."
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Label("Current Metric:"),
                        dbc.Spinner(
                            dbc.RadioItems(
                                id="metric-selector",
                                options=METRIC_OPTIONS,
                                value="net",
                                inline=True,
                            ),
                            color="success",
                        ),
                    ],
                    md=6,
                    xs=12,
                    className="mb-3",
                ),
            ]
        ),
        dbc.Row([dbc.Col(dcc.Graph(id="performance-graph"), width=12)]),
    ],
    fluid=True,
)


@callback(
    Output("swe-figure", "figure"), Input("segment-dropdown", "value")
)
def update_timeline(value):
    if value is None:
        return

    figure = go.Figure(
        layout=go.Layout(
            title=dict(text="Zonal SWE"),
            xaxis=dict(title="Date"),
            yaxis=dict(title="SWE (in)"),
            height=700,
        ),
    )

    for name, df_group in load_and_group(value):
        for dataset in DATASETS:
            figure.add_trace(add_scatter_line(df_group, dataset, name[6:8]))

    figure.update_traces(visible=True)
    figure.update_layout(template="plotly_white")

    return figure

@callback(
    Output("performance-graph", "figure"),
    Input("segment-dropdown", "value"),
    Input("metric-selector", "value"),
)
def update_graph(segment: Optional[str], metric: str) -> go.Figure | None:
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
