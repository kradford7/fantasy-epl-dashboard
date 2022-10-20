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
    stats = [
        stat for stat in
        list(list(dat['players'].values())[0]['matches'].values())[0].keys()
    ]
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
app.layout = dbc.Container(
    children=[
        dcc.Location(id='url'),
        dcc.Store(id='viewport-dims'),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Select(
                            id='select-stat',
                            value='total_points',
                            options=[
                                {
                                    'value': stat,
                                    'label': ' '.join(
                                        s.capitalize() for s in stat.split('_'))
                                } for stat in stats]),
                        dbc.Switch(id='switch-norm', label='Normalize'),
                        dbc.Switch(id='switch-cuml', label='Cumulative')],
                    id='sidebar',
                    className='bg-info',
                    style={
                        'height': 'inherit',
                        'padding': '2rem'},
                    width=2),
                dbc.Col(
                    children=html.Iframe(
                        id='chart',
                        style={
                            'border-width': 0,
                            'width': 'inherit',
                            'height': 'inherit',
                            'margin': 0,
                            'padding': 0}),
                    id='main',
                    style={
                        'height': 'inherit',
                        'padding': 0})],
            style={
                'height': 'inherit',
                'margin': 0})
    ] if data_loaded else 'Error. Data not found.',
    style={
        'width': '99vw',
        'height': '99vh',
        'padding': 0,
        'margin': 0},
    fluid=True
)


# Callback functions
app.clientside_callback(
    """
    function(_) {
        var w = document.getElementById("main").offsetWidth;
        var h = document.getElementById("main").offsetHeight;
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
