from requests import get
from time import sleep

import pandas as pd
import pickle


# Declare constants
__URL = 'https://fantasy.premierleague.com/api/'
ENDPOINTS = {
    'general': f'{__URL}bootstrap-static/',
    'fixtures': f'{__URL}fixtures/',
    'player': lambda player_id: f'{__URL}element-summary/{player_id}/'
}
DATA_PATH = './data.pkl'


# Construct data object
r = get(ENDPOINTS['general']).json()
dat = {
    'teams': {
        team['id']: {
            k: v for k, v in team.items() if k in [
                'name', 'short_name', 'strength']}
        for team in r['teams']},
    'positions': {
        position['id']: {
            k: v for k, v in position.items() if k in [
                'singular_name', 'singular_name_short']}
        for position in r['element_types']},
    'players': {
        player['id']: {
            k: v for k, v in player.items() if k in [
                'chance_of_playing_next_round',
                'chance_of_playing_this_round', 'element_type',
                'first_name', 'second_name', 'status', 'team', 'web_name',
                'minutes']}
        for player in r['elements']},
    'fixtures': {
        fixture['id']: {
            k: v for k, v in fixture.items() if k in [
                'finished', 'kickoff_time', 'team_a', 'team_a_score',
                'team_h', 'team_h_score']}
        for fixture in get(ENDPOINTS['fixtures']).json()}}

# Drop unavailable players
dat['players'] = {
    k: v for k, v in dat['players'].items() if v['status'] != 'u'}

# Drop players who have never played and drop 'minutes' stat
dat['players'] = {
    K: {k: v for k, v in V.items() if k != 'minutes'}
    for K, V in dat['players'].items() if V['minutes'] > 0}

# Drop unplayed fixtures and drop 'finished' indicator
dat['fixtures'] = {
    K: {k: v for k, v in V.items() if k != 'finished'}
    for K, V in dat['fixtures'].items() if V['finished']}

# Rename some keys for clarity
for position in dat['positions'].values():
    for old, new in {
        'singular_name': 'name',
        'singular_name_short': 'short_name'
    }.items():
        position[new] = position.pop(old)

for player in dat['players'].values():
    for old, new in {
        'element_type': 'position',
        'web_name': 'name'
    }.items():
        player[new] = player.pop(old)

# Collect player match data
print('collecting players...')
for id, player in dat['players'].items():
    sleep(0.1)
    player['matches'] = {
        match['round']: {
            k: v for k, v in match.items() if k in [
                'total_points', 'minutes', 'goals_scored', 'assists',
                'clean_sheets', 'goals_conceded', 'own_goals',
                'penalties_saved', 'penalties_missed', 'yellow_cards',
                'red_cards', 'saves', 'bonus', 'bps', 'value', 'selected']}
        for match in get(ENDPOINTS['player'](id)).json()['history']}

# Construct DataFrame from players
dat['players-df'] = pd.DataFrame(dat['players']).T[
    ['name', 'team', 'position', 'matches']]

# Convert team and position from index to name
dat['players-df']['team'] = dat['players-df']['team'].map(
    {k: v['name'] for k, v in dat['teams'].items()})

dat['players-df']['position'] = dat['players-df']['position'].map(
    {k: v['name'] for k, v in dat['positions'].items()})

# Convert match data from dict to DataFrame
dat['players-df']['matches'] = pd.Series(
    data=[
        pd.DataFrame(x).T.reset_index().rename(
            columns={'index': 'round', 'value': 'cost'})
        for x in dat['players-df']['matches']],
    index=dat['players-df'].index)

# Expand match data
for idx, matches in dat['players-df'].pop('matches').items():
  matches.index = [idx for _ in matches.index]
  matches[['name', 'team', 'position']] = dat['players-df'].loc[
    idx,
    ['name', 'team', 'position']]
  dat['players-df'] = pd.concat([dat['players-df'].drop(index=idx), matches])

# Convert dtypes
dat['players-df'].loc[:, 'round':] = \
    dat['players-df'].loc[:, 'round':].astype('int64')

# Save data
with open(DATA_PATH, 'wb') as f: pickle.dump(dat, f)
    
print('data saved successfully')
