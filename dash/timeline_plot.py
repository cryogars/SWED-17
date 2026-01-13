import pandas as pd
import plotly.graph_objects as go


COLORS = {
    'UF': 'steelblue',
    'MF': 'goldenrod',
    'LF': 'darkorchid',
    'OF': 'seagreen',
}
MM_IN_INCH = 25.4


def add_scatter_line(df_group: pd.DataFrame, product: str, zone_index: str):
    style_opts = {}
    if product == "iSnobal":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "8px 3px",
            },
        }
    elif product == "SNODAS":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "16px 3px",
            },
        }
    elif product == "UArizona":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "24px 3px",
            },
        }
    elif product == "CU Boulder":
        style_opts = {
            "mode": "markers",
            "marker": {
                "color": COLORS[zone_index],
                "symbol": "triangle-up",
                "size": 10,
            },
        }
    elif product == "ASO":
        style_opts = {
            "mode": "markers",
            "marker": {
                "color": COLORS[zone_index],
                "symbol": "circle",
                "size": 10,
            },
        }
    else:  # Snow-17
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "width": 3,
            },
        }

    return go.Scatter(
        x=df_group.index.tolist(),
        y=(df_group[product] / MM_IN_INCH),
        name=f"{product} {zone_index}",
        **style_opts,
    )

