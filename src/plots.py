import altair as alt
import pandas as pd


def plots(
    df:pd.DataFrame,
    dims:dict={'height': 500, 'width-pts': 500, 'width-lns': 500}, # TODO: remove
    stat:str='total_points',
    aggregate:str='weekly',
    pos:str=None
) -> alt.Chart:
    """
    Generates the main plots.
    
    Parameters
    ----------
    df : pandas.DataFrame
        players-df DataFrame from data.pkl
    dims : dict, optional
        plot dimensions. must contain keys 'height', 'width-pts' & 'width-lns'
    stat : str, optional
        a key in dat[player_id][matches] to visualise. Default 'total_points'
    aggregate : str, optional
        how to aggregate lines plot. Default 'weekly'
    pos : str, optional
        which position to focus on. Default None.

    Returns
    -------
    alt.Chart
        the generated plot.
    """
    stat_title = ' '.join(s.capitalize() for s in stat.split('_'))

    # Define the base upon which to build plots
    selector = alt.selection_multi(empty='none', fields=['name', 'position'])
    base = alt.Chart(
        df if pos is None else df[df['position'] == pos]
    ).add_selection(
        selector
    ).properties(
        height=dims['height']
    )

    # Define points plot [var(stat) vs sum(stat) facet by position]
    points = base.transform_aggregate(
        var=f'variance({stat})',
        sum=f'sum({stat})',
        latest='argmax(round)',
        groupby=['name', 'position']
    ).transform_calculate(
        value='datum.sum / datum.latest.cost'
    ).mark_circle(
    ).encode(
        x=alt.X(
            shorthand='sum:Q',
            axis=alt.Axis(format=' .2~s'),
            title=stat_title),
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
        tooltip=[
            alt.Tooltip(
                shorthand='name:N',
                title='Name'),
            alt.Tooltip(
                shorthand='sum:Q',
                title=stat_title),
            alt.Tooltip(
                shorthand='var:Q',
                format=' .2~s',
                title='Inconsistency'),
            alt.Tooltip(
                shorthand='value:Q',
                format=' .2~s',
                title='Value'),
            alt.Tooltip(
                shorthand='latest[cost]:Q',
                title='Cost')]
    ).properties(
        width=dims['width-pts' if pos is None else 'width-lns']
    )

    # Define lines plot [stat vs round for selected players]
    lines = base.mark_line(
        point=True
    ).transform_window(
        cumulative=f'sum({stat})',
        groupby=['name', 'position']
    ).transform_window(
        form=f'mean({stat})',
        groupby=['name', 'position'],
        sort=[alt.SortField(field='round', order='descending')]
    ).encode(
        x=alt.X(
            shorthand='round:Q',
            axis=alt.Axis(tickMinStep=1),
            scale=alt.Scale(domain=(1, df['round'].max())),
            title='Matchday'),
        y=alt.Y(
            shorthand=f"{stat if aggregate == 'weekly' else aggregate}:Q",
            axis=alt.Axis(format=' .2~s'),
            scale=alt.Scale(domain=(
                0,
                (
                    df.groupby('name').sum()
                    if aggregate == 'cumulative'
                    else df
                )[stat].max())),
            title=' '.join(s.capitalize() for s in stat.split('_'))),
        color=alt.Color(
            shorthand='name:N',
            title='Name'),
        tooltip=[
            alt.Tooltip(
                shorthand=f"{stat if aggregate == 'weekly' else aggregate}:Q",
                format=' .2~s',
                title=aggregate.capitalize() + ' ' + stat_title),
            alt.Tooltip(
                shorthand='minutes',
                title='Minutes')]
    ).transform_filter(
        selector
    ).properties(
        width=dims['width-lns']
    )

    # Concatenate charts and return
    return alt.vconcat(
        points,# if pos is None else alt.hconcat(points, points_form),
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
