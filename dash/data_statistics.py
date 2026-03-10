import numpy as np
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from scipy import integrate
from pandas import Series

from config import START_DATE, END_YEAR, DATASETS
from timeline_plot import MM_IN_INCH


def pairwise_statistics(data_a: Series, data_b: Series) -> dict:
    """
    Calculate similiarity statistics between the two given datasets.
    Current statistics:
    * Overlapping Index
    * Timing Shift
    * Relative Magnitude Ratio
    * Magnitude Difference (Area)
    * Mean Absolute Error

    Parameters
    ----------
    data_a : Series
        First dataset
    data_b : Series
        Second dataset

    Returns
    -------
    dict
        Calculated statistics
    """
    x = np.arange(0, len(data_b), 1)

    # Normalize (PDF)
    area_1 = integrate.simpson(data_a, x=x)
    area_2 = integrate.simpson(data_b, x=x)
    y1_norm = data_a / area_1
    y2_norm = data_b / area_2

    # Calculate centroids (mean time)
    y1_centroid = integrate.simpson(x * y1_norm, x=x)
    y2_centroid = integrate.simpson(x * y2_norm, x=x)

    # Overlapping index
    overlapping = integrate.simpson(np.minimum(y1_norm, y2_norm), x=x)
    # Timing shift (Positive show y1 being earlier in time)
    timing_shift = y1_centroid - y2_centroid
    # Relative Magnitude Ratio
    magnitude_ratio = area_2 / area_1
    # Magnitude Difference (Net Area)
    net_diff = area_2 - area_1
    # Root Mean Square Error
    rmse = np.sqrt(np.mean((data_b - data_a) ** 2))

    return {
        "overlapping": overlapping.round(2),
        "timing_shift": timing_shift.round(2),
        "magnitude": magnitude_ratio.round(2),
        "net": int(net_diff / MM_IN_INCH),
        "rmse": (rmse / MM_IN_INCH).round(2),
    }

def generate_statistics(data: pd.DataFrame) -> dict:
    """
    Calculate statistics broken down by water year

    Parameters
    ----------
    data : pd.DataFrame
        Daily SWE data

    Returns
    -------
    dict
        Dictionary with satistics for each year
    """
    cols = DATASETS[0:4]
    year_stats = {}

    for year in range(END_YEAR, int(START_DATE[0:4]), - 1):
        year_data = data[
            (data.index >= f"{year - 1}-10-01") & (data.index < f"{year}-10-01")
        ].sort_index()

        if len(year_data) < 1:
            continue

        overlapping = pd.DataFrame(index=cols, columns=cols).astype(float)
        timing_shift = pd.DataFrame(index=cols, columns=cols).astype(float)
        net_diff = pd.DataFrame(index=cols, columns=cols).astype(float)
        magnitude_diff = pd.DataFrame(index=cols, columns=cols).astype(float)
        rmse = pd.DataFrame(index=cols, columns=cols).astype(float)

        for col_a in cols:
            for col_b in cols:
                if col_a == col_b:
                    value = {
                        "overlapping": 1,
                        "timing_shift": 1,
                        "net": 1,
                        "magnitude": 1,
                        "rmse": 1,
                    }
                else:
                    value = pairwise_statistics(year_data[col_a], year_data[col_b])

                overlapping.loc[col_a, col_b] = value["overlapping"]
                timing_shift.loc[col_a, col_b] = value["timing_shift"]
                net_diff.loc[col_a, col_b] = value["net"]
                magnitude_diff.loc[col_a, col_b] = value["magnitude"]
                rmse.loc[col_a, col_b] = value["rmse"]

        year_stats[year] = {
            "timing_shift": timing_shift,
            "overlapping": overlapping,
            "magnitude": magnitude_diff,
            "net": net_diff,
            "rmse": rmse,
        }

    return year_stats

def plot_year(data: dict) -> go.Figure:
    """
    Plot statistics for all years of one zone

    Parameters
    ----------
    data : dict
        Statistics to plot

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    fig = make_subplots(
        rows=1,
        cols=5,
        shared_yaxes=True,
        subplot_titles=[
            "Timing Shift",
            "Overlapping Index",
            "Area Magnitude",
            "Total Net (in)",
            "RMSE (in/day)",
        ],
        horizontal_spacing=0.05,
    )
    column = 1

    for stat in data.values():
        # Mask symmetrical values
        mask = np.triu(np.ones(stat.shape), k=0).astype(bool)
        stat = stat.astype("string")
        stat[mask] = ""

        # Subset to reduce "NaN"
        stat = stat.iloc[1:4, 0:3]

        sub_fig = go.Heatmap(
            z=stat.values,
            y=stat.index,
            x=stat.columns,
            text=stat.values,
            texttemplate="%{text}",
            hoverongaps=False,
            coloraxis=f"coloraxis{column}",
            hoverinfo=["x", "y", "z"],
        )
        fig.add_trace(sub_fig, row=1, col=column)
        column += 1

    fig.update_layout(
        # Timing Shift
        coloraxis1=dict(
            colorscale="armyrose_r",
            cmid=0,
            colorbar_x=0.16,
            colorbar_thickness=10,
        ),
        # Overlapping Index
        coloraxis2=dict(
            colorscale="tempo_r",
            cmax=1,
            cmin=0.75,
            colorbar_x=0.37,
            colorbar_thickness=10
        ),
        # Area Magnitude
        coloraxis3=dict(
            colorscale="tealrose_r",
            cmid=1,
            colorbar_x=0.58,
            colorbar_thickness=10,
        ),
        # Total Net
        coloraxis4=dict(
            colorscale="tealrose_r",
            cmid=1,
            colorbar_x=0.79,
            colorbar_thickness=10,
        ),
        # Root Mean Square Error
        coloraxis5=dict(
            colorscale="tempo",
            colorbar_x=1,
            colorbar_thickness=10
        ),
    )

    return fig
