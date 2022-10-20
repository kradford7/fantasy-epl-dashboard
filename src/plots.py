import altair as alt
import numpy as np
import pandas as pd


def plots(
    dat:dict,
    dims:dict,
    stat:str='total_points',
    cumulative:bool=False
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
    cumulative : bool, optional
        whether to plot lines chart as cumulative. Default False.

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

    # Define the base upon which to build plots
    selector = alt.selection_multi(empty='none', fields=['name'])
    base = alt.Chart(
        df
    ).add_selection(
        selector
    ).properties(
        height=dims['height']
    )

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
            axis=alt.Axis(format=' .2~s'),
            title=' '.join(s.capitalize() for s in stat.split('_'))),
        y=alt.Y(
            shorthand='var:Q',
            axis=alt.Axis(labels=False, ticks=False),
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
        width=dims['width-pts']
    )

    # Define lines plot [stat vs round for selected players]
    lines = base.mark_line(
    ).transform_window(
        cuml_stat=f'sum({stat})',
        groupby=['name', 'position']
    ).encode(
        x=alt.X(
            shorthand='round:Q',
            axis=alt.Axis(tickMinStep=1),
            scale=alt.Scale(domain=(1, df['round'].max())),
            title='Matchday'),
        y=alt.Y(
            shorthand=f"{'cuml_stat' if cumulative else stat}:Q",
            axis=alt.Axis(format=' .2~s'),
            scale=alt.Scale(domain=(
                0,
                (df.groupby('name').sum() if cumulative else df)[stat].max())),
            title=' '.join(s.capitalize() for s in stat.split('_'))),
        color=alt.Color(
            shorthand='name:N',
            title='Name')
    ).transform_filter(
        selector
    ).properties(
        width=dims['width-lns']
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
