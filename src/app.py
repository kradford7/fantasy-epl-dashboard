from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import altair as alt
import dash_bootstrap_components as dbc
import pickle

from plots import plots


alt.data_transformers.disable_max_rows()

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

# Dashboard Layout
app.layout = dbc.Container(
    children=[
        dcc.Location(id='url'),
        dcc.Store(id='viewport-dims'),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='select-stat',
                            value='total_points',
                            clearable=False,
                            options=[
                                {
                                    'value': stat,
                                    'label': ' '.join(
                                        s.capitalize()
                                        for s in stat.split('_'))
                                } for stat in stats]),
                        html.P(
                            children='Stat',
                            className='text-primary'),
                        dcc.Dropdown(
                            id='select-agg',
                            value='weekly',
                            clearable=False,
                            searchable=False,
                            options=[
                                {'value': 'weekly', 'label': 'Weekly Values'},
                                {'value': 'cumulative', 'label': 'Cumulative'},
                                {'value': 'form', 'label': 'Form'}]),
                        html.P(
                            children='Bottom Chart Type',
                            className='text-primary'),
                        dcc.Dropdown(
                            id='select-pos',
                            searchable=False,
                            placeholder='None',
                            options=[
                                {
                                    'value': pos['name'],
                                    'label': pos['name']
                                } for pos in dat['positions'].values()]),
                        html.P(
                            children='Position Focus',
                            className='text-primary'),
                        html.Hr(
                            className='text-primary'),
                        html.P(
                            children='''
                                Click on a player in the top charts to view that
                                player's stats by matchday in the bottom chart.
                                Hold shift to select multiple players.''',
                            className='text-primary')],
                    id='sidebar',
                    class_name='bg-info',
                    style={
                        'height': 'inherit',
                        'padding': '1rem'},
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
    Input('select-agg', 'value'),
    Input('select-pos', 'value'),
    State('viewport-dims', 'data')
)
def update_chart(_, stat, agg, pos, dims):
    return plots(
        df=dat['players-df'],
        dims=dims,
        stat=stat,
        aggregate=agg,
        pos=pos
    ).to_html()


# Run app
if __name__ == '__main__': app.run()
