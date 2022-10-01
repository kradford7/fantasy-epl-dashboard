from datetime import datetime as dt
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import altair as alt
import dash_bootstrap_components as dbc

from get_data import get_data

# Declare constants
TODAY = dt.now().date()

# Declare dash app
app = Dash(
    name=__name__,
    title='Fantasy EPL Dashboard',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# app.config.suppress_callback_exceptions = True
server = app.server

# Configure Altair - uncomment to run locally, comment out for Heroku deployment
# alt.renderers.enable('mimetype')
# alt.data_transformers.enable('data_server')
# alt.data_transformers.disable_max_rows()

# Dashboard Layout
app.layout = html.Div(children=[
    dcc.Loading(
        id='main',  
        fullscreen=True),
    dcc.Store(
        id='local-data',
        storage_type='local'),
    dcc.Store(
        id='data-loaded',
        data=False)
])


# Callback functions
@app.callback(
    Output('main', 'children'),
    Output('data-loaded', 'data'),
    Output('local-data', 'data'),
    Input('data-loaded', 'data'),
    State('local-data', 'modified_timestamp'),
    State('local-data', 'data')
)
def load_data(data_loaded, tstamp, local_data):
    if data_loaded: raise PreventUpdate

    if dt.fromtimestamp(max(0, tstamp // 1000)).date() != TODAY:
        local_data = get_data()
    
    child = local_data['teams']['1']['name']

    return child, True, local_data


# Run app
if __name__ == '__main__': app.run_server(debug=True)
