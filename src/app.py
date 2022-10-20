from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import pickle

from plots import plots


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

server = app.server

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
                                        s.capitalize()
                                        for s in stat.split('_'))
                                } for stat in stats]),
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
                            'width': '95%',
                            'height': '95%',
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
        'width': '100vw',
        'height': '100vh',
        'padding': 0,
        'margin': 0},
    fluid=True
)


# Callback functions
app.clientside_callback(
    """
    function(_) {
        var w = document.getElementById("chart").offsetWidth;
        var h = document.getElementById("chart").offsetHeight;

        return {
            'height': Math.floor(0.36 * h),
            'width-pts': Math.floor(0.2 * w),
            'width-lns': Math.floor(0.86 * w)
        };
    }
    """,
    Output('viewport-dims', 'data'),
    Input('url', 'pathname')
)

@app.callback(
    Output('chart', 'srcDoc'),
    Input('viewport-dims', 'modified_timestamp'),
    Input('select-stat', 'value'),
    Input('switch-cuml', 'value'),
    State('viewport-dims', 'data')
)
def update_chart(_, stat, cuml, dims):
    return plots(
        dat=dat,
        dims=dims,
        stat=stat,
        cumulative=cuml
    ).to_html()


# Run app
if __name__ == '__main__': app.run_server(debug=True)
