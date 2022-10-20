import altair as alt
import numpy as np
import pandas as pd


def plots(
    dat:dict,
    dims:dict,
    stat:str='total_points',
    inv_norm:bool=False
) -> alt.Chart:
    """
    Generates the main plots.
    
    Parameters
    ----------
    dat : dict
        data as loaded from data.pkl
    dims : dict
        plot dimensions. must contain keys 'height' and 'width'
    stat : str, optional
        a key in dat[player_id][matches] to visualise. Default 'total_points'
    inv_norm : bool, optional
        whether to normalize the data such that [0, 0] represents most prolific
        and most consistent and [1, 1] is the opposite. Default False.

    Returns
    -------
    alt.Chart
        the generated plot.
    """
    # Construct dataframe template
    df = pd.DataFrame(
        columns=['name', 'position', 'round', stat, 'cost'])

    # Add each match per player to dataframe
    for player in dat['players'].values():
        for round, match in player['matches'].items():
            if match['minutes'] > 0:
                df.loc[len(df)] = [
                    player['name'],
                    player['position'],
                    round,
                    match[stat],
                    match['value']
                ]

    # Convert position ids to names
    df['position'] = df['position'].map(
        {k: v['name'] for k, v in dat['positions'].items()}
    )

    # Normalize 'sum' and 'var' columns if indicated
    # if inv_norm:
    #     df[stat] = 1 - (
    #         (df[stat] - df[stat].min())
    #         / (df[stat].max() - df[stat].min())
    #     )

    #     df['inconsistency'] = (
    #         (df['inconsistency'] - df['inconsistency'].min())
    #         / (df['inconsistency'].max() - df['inconsistency'].min())
    #     )

    # Generate x label if not given
    # if x_lab is None:
    #     x_lab = (
    #         'Normalized Inverse ' if inv_norm
    #         else '' if stat.startswith('total')
    #         else 'Total '
    #     )
    #     x_lab += ' '.join(s.capitalize() for s in stat.split('_'))

    # Define the base upon which to build plots
    selector = alt.selection_multi(empty='none', fields=['name'])
    base = alt.Chart(df).add_selection(selector)

    # Define points plot [var(stat) vs sum(stat) facet by position]
    points = base.transform_aggregate(
        var=f'variance({stat})',
        sum=f'sum({stat})',
        current_cost='max(cost)',   # TODO: somehow get latest cost
        groupby=['name', 'position']
    ).transform_calculate(
        value='datum.sum / datum.current_cost'
    ).mark_circle(
    ).encode(
        x=alt.X(
            shorthand='sum:Q',
            title=' '.join(s.capitalize() for s in stat.split('_'))),
        y=alt.Y(
            shorthand='var:Q',
            title='Inconsistency'),
        opacity=alt.condition(
            predicate=selector,
            if_true=alt.value(1.0),
            if_false=alt.Opacity('value:Q', legend=None)),
        color=alt.condition(
            predicate=selector,
            if_true=alt.value('red'),
            if_false=alt.Color('value:Q', legend=None, sort='descending')),
        column=alt.Column(
            shorthand='position:O',
            sort=['Goalkeeper', 'Defender', 'Midfielder', 'Forward'],
            title=None),
        tooltip=['name:N', 'sum:Q', 'var:Q', 'value:Q']
    ).properties(
        width=np.floor(0.85 * dims['width']) // 4,
        height=np.floor(0.38 * dims['height'])
    )

    # Define lines plot [stat vs round for selected players]
    lines = base.mark_line(
    ).encode(
        x=alt.X(
            shorthand='round:Q',
            axis=alt.Axis(tickMinStep=1),
            scale=alt.Scale(domain=(1, df['round'].max())),
            title='Matchday'),
        y=alt.Y(
            shorthand=f'{stat}:Q',
            scale=alt.Scale(domain=(0, df[stat].max())),    # TODO: add option to display cumulative plot
            title=' '.join(s.capitalize() for s in stat.split('_'))),
        color=alt.Color(
            shorthand='name:N',
            title='Name')
    ).transform_filter(
        selector
    ).properties(
        width=np.floor(0.9 * dims['width']),
        height=np.floor(0.38 * dims['height'])
    )

    # Concatenate charts and return
    return alt.vconcat(
        points,
        lines
    ).configure(
        background='#FFF0'
    ).configure_axis(
        grid=False,
        labelColor='lightgrey',
        titleColor='lightgrey'
    ).configure_header(
        labelColor='lightgrey'
    ).configure_view(
        strokeWidth=0
    ).configure_legend(
        labelColor='lightgrey',
        titleColor='lightgrey',
        orient='top-right'
    )
