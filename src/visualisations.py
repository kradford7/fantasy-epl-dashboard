import altair as alt
import numpy as np
import pandas as pd


def var_vs_sum(
    dat:dict,
    stat:str='total_points',
    inv_norm:bool=False,
    x_lab:str=None
) -> alt.Chart:
    """
    Generates a plot of variance vs sum of some defined stat.
    
    Parameters
    ----------
    dat : dict
        data as loaded from data.pkl
    stat : str, optional
        a key in dat[player_id][matches] to visualise. Default 'total_points'
    inv_norm : bool, optional
        whether to normalize the data such that [0, 0] represents most prolific
        and most consistent and [1, 1] is the opposite. Default False.
    x_lab : str, optional
        the desired label on the x axis

    Returns
    -------
    alt.Chart
        the generated plot.
    """
    # Construct dataframe template
    df = pd.DataFrame(
        columns=['name', stat, 'inconsistency', 'cost', 'position'])

    # Add each player to dataframe
    for player in dat['players'].values():
        # Collect stat for each match that player played in
        stats = [
            match[stat]
            for match in player['matches'].values()
            if match['minutes'] > 0
        ]

        # Get player info, calculate sum & var then add player to dataframe
        df.loc[len(df)] = [
            player['name'],
            np.sum(stats),
            np.var(stats),
            player['matches'][max(player['matches'].keys())]['value'],
            player['position']
        ]

    # Calculate player value (stat / cost)
    df['value'] = df[stat] / df['cost']

    # Convert position numbers to names
    df['position'] = df['position'].map(
        {k: v['name'] for k, v in dat['positions'].items()}
    )

    # Normalize 'sum' and 'var' columns if indicated
    if inv_norm:
        df[stat] = 1 - (
            (df[stat] - df[stat].min())
            / (df[stat].max() - df[stat].min())
        )

        df['inconsistency'] = (
            (df['inconsistency'] - df['inconsistency'].min())
            / (df['inconsistency'].max() - df['inconsistency'].min())
        )

    # Generate x label if not given
    if x_lab is None:
        x_lab = (
            'Normalized Inverse ' if inv_norm
            else '' if stat.startswith('total')
            else 'Total '
        )
        x_lab += ' '.join(s.capitalize() for s in stat.split('_'))

    # Generate chart and return
    return alt.Chart(
        df
    ).mark_circle(
    ).encode(
        x=alt.X(
            shorthand=f'{stat}:Q',
            title=x_lab),
        y=alt.Y(
            shorthand='inconsistency:Q',
            title=(inv_norm * 'Normalized ' + 'Inconsistency')),
        opacity='value:Q',
        color=alt.Color(
            shorthand='value:Q',
            legend=None,
            sort='descending'),
        column=alt.Column(
            shorthand='position:N',
            sort=['Goalkeeper', 'Defender', 'Midfielder', 'Forward'],
            title=None),
        tooltip=['name:N', f'{stat}:Q', 'inconsistency:Q', 'value:Q']
    ).configure(
        background='#FFF0'
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    )
