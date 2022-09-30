from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from requests import get

import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

from get_data import ENDPOINTS, get_data


dat = get_data()

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
app.layout = dbc.Container(
    id='body',
    children=[
        dcc.Location(id='url'),
        dcc.Interval(
            id='get-players',
            interval=100,
            n_intervals=0,
            max_intervals=len(dat['players'].index)-1
            ),
        dbc.Progress(
            id='progress-bar',
            value=0
            ),
        html.Iframe(
            id='scatter',
            style={'border-width': '0', 'width': '100%', 'height': '400px'}
            )
    ],
    fluid=True
)

# Callback functions
@app.callback(
    Output('progress-bar', 'value'),
    Output('progress-bar', 'label'),
    Input('get-players', 'n_intervals'),
    State('get-players', 'max_intervals')
)
def load_data(n, N):
    id = dat['players'].index[n]
    dat['players-hist'] = pd.concat(
        objs=[
            dat['players-hist'],
            pd.DataFrame(get(ENDPOINTS['player'](id)).json()['history'])[[
                'element', 'total_points', 'round', 'minutes',
                'goals_scored', 'assists', 'clean_sheets',
                'goals_conceded', 'own_goals', 'penalties_saved',
                'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
                'bonus', 'bps', 'value', 'selected'
            ]].rename(columns={'element': 'player_id'})
        ],
        ignore_index=True
    )

    progress = round(n / N * 100)
    msg = f'{n} of {N} players loaded...' if n < N else 'All players loaded!'

    return progress, msg


@app.callback(
    Output('scatter', 'srcDoc'),
    Input('get-players', 'n_intervals'),
    State('get-players', 'max_intervals')
)
def plot_altair(n, N):
    if n >= N:
        df = pd.merge(
            left=dat['players-hist'][[
                    'player_id', 'total_points'
                ]].groupby(
                    'player_id', sort=False
                ).agg(
                    ['mean', 'var']
                ).dropna(
                ).droplevel(
                    0, axis=1
                ),
            right=dat['players']['name'],
            left_index=True,
            right_index=True
        )

        return alt.Chart(df).mark_point().encode(
            x='mean:Q',
            y='var:Q',
            tooltip=['name:N', 'mean:Q', 'var:Q']
        ).interactive().to_html()
    else:
        return None

# Run app
if __name__ == '__main__': app.run_server(debug=True)
