from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import altair as alt
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pickle

import visualisations as vis


# Load data
try:
    with open('./data.pkl', 'rb') as f: dat = pickle.load(f)
except:
    data_loaded = False
else:
    data_loaded = True

# Declare dash app
app = Dash(
    name=__name__,
    title='Fantasy EPL Dashboard',
    external_stylesheets=[dbc.themes.SLATE],
    suppress_callback_exceptions=True
)

# app.config.suppress_callback_exceptions = True
server = app.server

# Configure Altair - uncomment to run locally, comment out for Heroku deployment
# alt.renderers.enable('mimetype')
# alt.data_transformers.enable('data_server')
# alt.data_transformers.disable_max_rows()

# Dashboard Layout
app.layout = html.Div(
    id='main',
    children=[
        dcc.Location(id='url'),
        html.Iframe(
            id='chart',
            style={
                'border-width': '0',
                'width': '100%',
                'height': '625px',
                'display': 'block',
                'margin': '0 auto'}),
        # dbc.Select(
        #     id='stat-select',
        #     value='total_points',
        #     options=[
        #         {
        #             'label': ' '.join(s.capitalize() for s in stat.split('_')),
        #             'value': stat}
        #         for stat in list(list(
        #             dat['players'].values())[0]['matches'].values())[0]]),
        # dbc.Switch(
        #     id='inv-norm',
        #     label="""Normalize chart such that most prolific and consistent is
        #         located at (0, 0)""",
        #     value=False)
    ] if data_loaded else 'Error. Data not found.'
)


# Callback functions
@app.callback(
    Output('chart', 'srcDoc'),
    Input('url', 'pathname')
    # Input('stat-select', 'value'),
    # Input('inv-norm', 'value')
)
def update_chart(_):#stat, inv_norm):
    return vis.plots(
        dat=dat,
        # stat=stat,
        # inv_norm=inv_norm
    ).to_html()


# Run app
if __name__ == '__main__': app.run_server(debug=True)
