from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd
import requests

# Define API endpoints
url = 'https://fantasy.premierleague.com/api/'

endpoints = {
	'general'			: f'{url}bootstrap-static/',
	'fixtures'			: f'{url}fixtures/',
	'player-data'		: lambda player_id: f'{url}element-summary/{player_id}/',
	'manager'			: lambda manager_id: f'{url}entry/{manager_id}/',
	'manager-history'	: lambda manager_id: f'{url}entry/{manager_id}/history/'
}

# Get player data
r = requests.get(endpoints['general'])

players_df = pd.DataFrame(r.json()['elements'])[['web_name', 'team', 'element_type', 'now_cost', 'minutes', 'value_season', 'total_points', 'id', 'points_per_game']]

players_df.loc[:, ('element_type')] = players_df['element_type'].map(pd.DataFrame(r.json()['element_types']).set_index('id')['singular_name'])
players_df.loc[:, ('team')]         = players_df['team'].map(pd.DataFrame(r.json()['teams']).set_index('id')['name'])
players_df.loc[:, ('value_season')] = players_df['value_season'].astype(float)
players_df.rename(columns={'web_name': 'player', 'element_type': 'position'}, inplace=True)

# Declare dash app
app = Dash(
	name	= __name__,
	title	= 'Fantasy EPL Dashboard'
)

# app.config.suppress_callback_exceptions = True
server = app.server

# Configure Altair - uncomment to run locally, comment out for Heroku deployment
# alt.renderers.enable('mimetype')
# alt.data_transformers.enable('data_server')
# alt.data_transformers.disable_max_rows()

# Dashboard Layout
app.layout = dbc.Container(
	children = [
		dcc.Location(id='url'),
		html.Iframe(id='scatter', style={'border-width': '0', 'width': '100%', 'height': '400px'})
	],
	fluid = True
)

# Callback functions
@app.callback(
	Output('scatter', 'srcDoc'),
	Input('url', 'pathname')
)
def plot_altair(_):
	return alt.Chart(players_df).mark_point().encode(
		x = 'minutes:O',
		y = 'total_points:O',
		color = 'position'
	).interactive().to_html()

# Run app
if __name__ == '__main__': app.run_server(debug=True)
