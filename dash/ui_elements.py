from dash import html, dcc

from data_load import available_zones

def zone_dropdown():
    zones = available_zones()
    basin_values = [name for name in zones["Segment"].unique()]
    options = [
        {
            "label": f"{name[0:4]} - {zones[zones['Segment'] == name].iloc[0]['Description']}",
            "value": name,
        }
        for name in basin_values
    ]

    return [
        html.P("Select zone"),
        dcc.Dropdown(
            id="segment-dropdown",
            options=options,
            clearable=True,
            placeholder="Select a zone",
        ),
    ]
