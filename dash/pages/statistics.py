import dash
from dash import callback, html, dcc, Input, Output
from typing import Optional

from psycopg import sql

import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly.graph_objects import Figure

from nb_paths import SWE_DB
from ui_elements import zone_dropdown
from data_load import available_zones

STATS_QUERY = """
SELECT cbrfc_id, year, name, {} from swe_metrics where cbrfc_id in ({});
"""

dash.register_page(__name__, path="/statistics")

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("SWE Model Performance Metrics", className="text-center my-4"),
                width=12
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
                            options=[
                                {"label": "MAE", "value": "mae"},
                                {"label": "Net Change", "value": "net"},
                                {"label": "Magnitude", "value": "magnitude"},
                            ],
                            value="mae",
                            inline=True,
                        ),
                    ],
                    md=6,
                    xs=12,
                    className="mb-3",
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="performance-graph"),
                width=12
            )
        ),
    ],
    fluid=True,
)

@callback(
    Output("performance-graph", "figure"),
    Input("segment-dropdown", "value"),
    Input("metric-selector", "value"),
)
def update_graph(segment: Optional[str], metric: str) -> Figure | None:
    """Update the statistics figure with the selected segment and metric.

    Args:
        segment: Selected zone segment from the dropdown.
        metric: Metric column name to plot.

    Returns:
        Plotly Figure object or None if no segment is passed in.
    """
    if segment is None:
        return None

    zones = available_zones()
    zones = zones[zones.Segment == segment]
    query = sql.SQL(STATS_QUERY).format(
        sql.Identifier(metric),
        sql.SQL(",").join(map(sql.Literal, zones.index.values))
    )
    with SWE_DB.query(query) as results:
        columns = [c.name for c in results.description]
        df = pd.DataFrame(results.fetchall(), columns=columns).set_index("cbrfc_id")

    df = pd.merge(df, zones, left_index=True, right_index=True, how="left")

    # Create Grouped Bar Chart
    fig = px.bar(
        df,
        x="year",
        y=metric,
        color="name",
        barmode="group",
        facet_col="Zone Name",
        labels={
            "year": "Year",
            metric: metric.upper(),
            "name": "Model",
        },
        template="plotly_white",
    )

    fig.update_layout(transition_duration=300)
    return fig
