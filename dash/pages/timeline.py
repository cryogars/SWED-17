import dash
from dash import dcc, html, Input, Output, callback

import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from config import DATASETS
from data_load import load_and_group
from timeline_plot import add_scatter_line
from ui_elements import zone_dropdown
from data_statistics import generate_statistics, plot_year

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
        # dbc.Row(
        #     dbc.Col(
        #         [
        #             html.H3("Yearly Statistics", className="mt-4"),
        #             dbc.Spinner(
        #                 html.Div(id="swe-stats"),
        #                 color="success",
        #             ),
        #         ]
        #     )
        # ),
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

# @callback(
#     Output("swe-stats", "children"), [Input("segment-dropdown", "value")]
# )
def update_stats(value):
    children = []
    year_stats = {}

    if value is None:
        return children

    for name, df_group in load_and_group(value):
        year_stats[name] = generate_statistics(df_group)

    for zone_name, all_years in year_stats.items():
        accordion_years = []
        for year, data in all_years.items():
            accordion_years.append(
                dbc.AccordionItem(
                    dcc.Graph(figure=plot_year(data)),
                    title=year,
                )
            )

        children.append(
            dbc.Row(
                dbc.Col(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            dbc.Accordion(
                                accordion_years,
                                start_collapsed=True,
                            ),
                            title=zone_name,
                        ),
                        start_collapsed=True,
                    )
                ),
                className="mt-4",
            )
        )

    return children
