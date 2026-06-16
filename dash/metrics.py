from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from data_load import available_zones
from nb_paths import SWE_DB
from plotly.graph_objects import Figure
from psycopg import sql

from dash import html

METRIC_OPTIONS = [
    {
        "label": html.Span(
            [
                "Net Difference",
                dbc.Tooltip(
                    "The difference in total SWE by the end of the season.",
                    target="tooltip-net",
                    placement="top",
                ),
            ],
            id="tooltip-net",
        ),
        "value": "net",
    },
    {
        "label": html.Span(
            [
                "Magnitude",
                dbc.Tooltip(
                    "The ratio of total SWE by the end of the season.",
                    target="tooltip-magnitude",
                    placement="top",
                ),
            ],
            id="tooltip-magnitude",
        ),
        "value": "magnitude",
    },
    {
        "label": html.Span(
            [
                "Mean Daily Difference",
                dbc.Tooltip(
                    "The average of the absolute daily differences in SWE.",
                    target="tooltip-mae",
                    placement="top",
                ),
            ],
            id="tooltip-mae",
        ),
        "value": "mae",
    },
]

STATS_QUERY = """
SELECT sm.cbrfc_id, sm.year, sm.name, sm.{}, cz.zone AS "Zone Name"
FROM swe_metrics sm
LEFT JOIN cbrfc_zones cz ON sm.cbrfc_id = cz.gid
WHERE sm.cbrfc_id in ({});
"""

def metric_bar_chart(segment: Optional[str], metric: str) -> Figure | None:
    """
    Build a grouped bar chart of metric values for zones in a segment.

    Args:
        segment: Selected zone segment from the dropdown.
        metric: Metric column name to plot.

    Returns:
        Plotly Figure object or None if no segment is passed in.
    """
    zones = available_zones()
    zones = zones[zones.Segment == segment]
    query = sql.SQL(STATS_QUERY).format(
        sql.Identifier(metric),
        sql.SQL(",").join(map(sql.Literal, zones.index.values)),
    )
    with SWE_DB.query(query) as results:
        columns = [c.name for c in results.description]
        df = pd.DataFrame(results.fetchall(), columns=columns).set_index(
            "cbrfc_id"
        )

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

    if metric == "magnitude":
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color="black",
        )

    fig.update_layout(transition_duration=300)

    return fig


TABLE_DATA_QUERY = """
SELECT  cz.zone AS "Zone Name", sm.year, sm.name, sm.magnitude, sm.net, sm.mae, cc.description
FROM swe_metrics sm
LEFT JOIN cbrfc_zones cz ON sm.cbrfc_id = cz.gid
LEFT JOIN cbrfc_ch5id cc ON cz.ch5_id = cc.id
"""
TABLE_DATA_COLUMNS = [
    "Zone Name",
    "Year",
    "Data Source",
    "Magnitude",
    "Net Difference",
    "Mean Daily Difference",
    "Segment",
]


def metric_table_data():
    with SWE_DB.query(TABLE_DATA_QUERY) as results:
        return pd.DataFrame(results.fetchall(), columns=TABLE_DATA_COLUMNS)
