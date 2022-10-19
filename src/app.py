from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import altair as alt
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pickle

import plots


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

# Dashboard Layout  TODO: consider dbc.Col(xs, xm) params for mobile interface
app.layout = html.Div(
    children=[
        dcc.Location(id='url'),
        html.Iframe(
            id='chart',
            style={
                'border-width': 0,
                'width': '100vw',
                'height': '100vh',
                'display': 'block',
                'margin': 0,
                'padding': 0}),
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
        #     value=False),
        dcc.Store(id='viewport-dims')
    ] if data_loaded else 'Error. Data not found.',
    style={
        'width': 'inherit',
        'height': 'inherit',
        'margin': 0,
        'padding': 0}
)


# Callback functions
app.clientside_callback(
    """
    function(_) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return {'height': h, 'width': w};
    }
    """,
    Output('viewport-dims', 'data'),
    Input('url', 'pathname')
)

@app.callback(
    Output('chart', 'srcDoc'),
    Input('viewport-dims', 'modified_timestamp'),
    State('viewport-dims', 'data'),
    # Input('stat-select', 'value'),
    # Input('inv-norm', 'value')
)
def update_chart(_, dims):#stat, inv_norm):
    return plots.plots(
        dat=dat,
        dims=dims,
        # stat=stat,
        # inv_norm=inv_norm
    ).to_html()


# Run app
if __name__ == '__main__': app.run_server(debug=True)
