import pandas as pd
import requests

# Define API endpoints
__url = 'https://fantasy.premierleague.com/api/'
ENDPOINTS = {
    'general': f'{__url}bootstrap-static/',
    'player': lambda player_id: f'{__url}element-summary/{player_id}/'
}


# Functions
def get_players() -> pd.DataFrame:
    """Returns player data collected from API in a DataFrame."""
    dat = requests.get(ENDPOINTS['general']).json()
    df = pd.DataFrame(dat['elements']).set_index('id')

    # Only keep certain columns
    df = df[['chance_of_playing_next_round', 'chance_of_playing_this_round',
        'element_type', 'first_name', 'now_cost', 'second_name', 'status',
        'team', 'web_name'
    ]]

    # Drop unavailable players
    df = df[df['status'] != 'u']

    # Rename element_type to position for clarity
    df.rename(columns={'element_type': 'position'}, inplace=True)

    # Change position and team IDs to relevant names
    df.loc[:, ['position']] = df['position'].map(
        pd.DataFrame(dat['element_types']).set_index('id')['singular_name'])
    df.loc[:, ['team']] = df['team'].map(
        pd.DataFrame(dat['teams']).set_index('id')['short_name'])

    return df


def get_player_history(id: int) -> pd.DataFrame:
    """Returns player data for past games in a DataFrame."""
    dat = requests.get(ENDPOINTS['player'])


# Save data to CSV if script is run
if __name__ == '__main__':
    get_players().to_csv('data.csv')
