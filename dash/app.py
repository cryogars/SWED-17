#!/usr/bin/env python
# coding: utf-8

import sys
import os
import dash

from nb_paths import HOST_IP
from dash import Dash
import dash_bootstrap_components as dbc

# Dash App
# --------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.ZEPHYR],
    use_pages=True,
    pages_folder=os.path.join(os.path.dirname(__file__), "pages"),
)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                page["name"], href=page["relative_path"], active="exact"
            )
        )
        for page in dash.page_registry.values()
    ],
    brand="SWE Datasets",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4",
)

app.layout = dbc.Container([navbar, dash.page_container], fluid=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        app.run(host="0.0.0.0", debug=True)
    else:
        app.run(host=HOST_IP)