import altair as alt
import numpy as np
import pandas as pd


def var_vs_sum(
    dat:dict,
    stat:str,
    inv_norm:bool=False,
    x_lab:str=None
) -> alt.Chart:
    """
    Generates a plot of variance vs sum of some defined stat.
    
    Parameters
    ----------
    dat : dict
        player data as collected from get_data.get_data()['players']
    stat : str
        a key in dat[player_id][matches] to visualise.
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
    df = pd.DataFrame(columns=['name', 'sum', 'var'])
    for player in dat.values():
        stats = [
            match[stat]
            for match in player['matches'].values()
            if match['minutes'] > 0
        ]
        df.loc[len(df)] = [player['name'], np.sum(stats), np.var(stats)]

    if inv_norm:
        df['sum'] = (
            1
            - (df['sum'] - df['sum'].min())
            / (df['sum'].max() - df['sum'].min())
        )

        df['var'] = (
            (df['var'] - df['var'].min())
            / (df['var'].max() - df['var'].min())
        )

    if x_lab is None:
        x_lab = (
            'Inverse ' if inv_norm
            else '' if stat.startswith('total')
            else 'Total '
        )
        x_lab += ' '.join(s.capitalize() for s in stat.split('_'))

    return alt.Chart(df).mark_point().encode(
        x=alt.X('sum:Q', title=x_lab),
        y=alt.Y('var:Q', title='Inconsistency'),
        tooltip=['name:N']
    )
