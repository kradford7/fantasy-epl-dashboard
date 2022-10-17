from datetime import datetime as dt
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import altair as alt
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd

# from get_data import get_data

# import visualisations as vis

# Declare constants
TODAY = dt.now().date()

# Declare dash app
app = Dash(
    name=__name__,
    title='Fantasy EPL Dashboard',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# app.config.suppress_callback_exceptions = True
server = app.server

# Configure Altair - uncomment to run locally, comment out for Heroku deployment
# alt.renderers.enable('mimetype')
# alt.data_transformers.enable('data_server')
# alt.data_transformers.disable_max_rows()

# Dashboard Layout
app.layout = html.Div([
    html.Div(
        id='main'),
    dcc.Loading(
        id='data-loading',
        fullscreen=True,
        children=[
            dcc.Store(
                id='local-data',
                storage_type='local'
            ),
            dcc.Store(
                id='data-loaded',
                data=False
            )
        ]
    )
    # dcc.Store(
    #     id='local-data',
    #     storage_type='local'),
    # dcc.Store(
    #     id='data-loaded',
    #     data=False)
])


# Callback functions
# @app.callback(
#     Output('main', 'children'),
#     Output('data-loaded', 'data'),
#     Output('local-data', 'data'),
#     Input('data-loaded', 'data'),
#     State('local-data', 'modified_timestamp'),
#     State('local-data', 'data')
# )
# def load_data(data_loaded, t, dat):
#     if data_loaded: raise PreventUpdate
#     if dt.fromtimestamp(max(0, t // 1000)).date() != TODAY: dat = get_data()

#     content = [
#         html.Iframe(
#             id='chart',
#             style={
#                 'border-width': '0',
#                 'width': '500px',
#                 'height': '400px',
#                 'display': 'block',
#                 'margin': '0 auto'}),
#         dbc.Select(
#             id='stat-select',
#             value='total_points',
#             options=[
#                 {
#                     'label': ' '.join(s.capitalize() for s in stat.split('_')),
#                     'value': stat}
#                 for stat in list(list(
#                     dat['players'].values())[0]['matches'].values())[0]]),
#         dbc.Switch(
#             id='inv-norm',
#             label="""Normalize chart such that most prolific and consistent is
#                 located at (0, 0)""",
#             value=False)
#     ]

#     return content, True, dat


# @app.callback(
#     Output('chart', 'srcDoc'),
#     Input('stat-select', 'value'),
#     Input('inv-norm', 'value'),
#     State('local-data', 'data')
# )
# def update_chart(stat, inv_norm, dat):
#     return vis.var_vs_sum(
#         dat=dat['players'],
#         stat=stat,
#         inv_norm=inv_norm
#     ).interactive().to_html()


# Run app
if __name__ == '__main__': app.run_server(debug=True)
