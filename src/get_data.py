from requests import get
from time import sleep

import pandas as pd

# Global constants
__url = 'https://fantasy.premierleague.com/api/'
ENDPOINTS = {
    'general': f'{__url}bootstrap-static/',
    'fixtures': f'{__url}fixtures/',
    'player': lambda player_id: f'{__url}element-summary/{player_id}/'
}


# Functions
def get_data(run_quick=False) -> dict:
    """Returns player data collected from API."""
    print('Oh boy, here I go!')
    r = get(ENDPOINTS['general']).json()

    dat = {
        'teams': pd.DataFrame(r['teams'])[[
                'id', 'name', 'short_name', 'strength'
            ]].set_index('id'),
        'positions': pd.DataFrame(r['element_types'])[[
                'id', 'singular_name', 'singular_name_short'
            ]].set_index('id').rename(columns={
                'singular_name': 'name', 'singular_name_short': 'short_name'
            }),
        'players': pd.DataFrame(r['elements'])[[
                'chance_of_playing_next_round', 'chance_of_playing_this_round',
                'element_type', 'first_name', 'id', 'second_name', 'status',
                'team', 'web_name'
            ]].set_index('id').rename(columns={
                'element_type': 'position', 'web_name': 'name'
            }),
        'fixtures': pd.DataFrame(get(ENDPOINTS['fixtures']).json())[[
                'finished', 'id', 'kickoff_time', 'team_a', 'team_a_score',
                'team_h', 'team_h_score'
        ]],
        'players-hist': pd.DataFrame()
    }

    # Drop unavailable players
    dat['players'] = dat['players'][dat['players']['status'] != 'u']

    # Drop unplayed fixtures and finished column
    dat['fixtures'] = dat['fixtures'].loc[
        dat['fixtures']['finished'],
        dat['fixtures'].columns.drop('finished')
    ]

    # Convert datetime object
    dat['fixtures']['kickoff_time'] = pd.to_datetime(
        dat['fixtures']['kickoff_time']
    )

    # Collect historical player data
    # for id in ([318, 427, 104, 80, 335] if run_quick else dat['players'].index):
    #     sleep(0.1)
    #     dat['players-hist'] = pd.concat(
    #         objs=[
    #             dat['players-hist'],
    #             pd.DataFrame(get(ENDPOINTS['player'](id)).json()['history'])[[
    #                 'element', 'total_points', 'round', 'minutes',
    #                 'goals_scored', 'assists', 'clean_sheets',
    #                 'goals_conceded', 'own_goals', 'penalties_saved',
    #                 'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
    #                 'bonus', 'bps', 'value', 'selected'
    #             ]].rename(columns={'element': 'player_id'})
    #         ],
    #         ignore_index=True
    #     )

    return dat


if __name__ == '__main__': pass
