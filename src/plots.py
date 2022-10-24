from cgitb import text
import altair as alt
import pandas as pd


def plots(
    df:pd.DataFrame,
    dims:dict,
    stat:str='total_points',
    cumulative:bool=False,
    pos:str=None
) -> alt.Chart:
    """
    Generates the main plots.
    
    Parameters
    ----------
    df : pandas.DataFrame
        players-df DataFrame from data.pkl
    dims : dict
        plot dimensions. must contain keys 'height' and 'width'
    stat : str, optional
        a key in dat[player_id][matches] to visualise. Default 'total_points'
    cumulative : bool, optional
        whether to plot lines chart as cumulative. Default False.
    pos : str, optional
        which position to focus on. Default None.

    Returns
    -------
    alt.Chart
        the generated plot.
    """
    stat_title = ' '.join(s.capitalize() for s in stat.split('_'))

    # Define the base upon which to build plots
    selector = alt.selection_multi(empty='none', fields=['name'])
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
        width=dims['width-pts']
    )

    # Define form plot
    # points_form = base.transform_window(
    #     l1=f'lag({stat},1)',
    #     l2=f'lag({stat},2)',
    #     l3=f'lag({stat},3)',
    #     l4=f'lag({stat},4)',
    #     groupby=['name', 'position']
    # ).transform_aggregate(
    #     latest='max(round)'
    # ).transform_filter(
    #     alt.datum.round == alt.datum.latest
    # ).transform_calculate(
    #     form3=f'(datum.l1+datum.l2+{stat}) / (3*mean({stat}))',
    #     form5=f'(datum.l1+datum.l2+datum.l3+datum.l4+{stat} / (3*mean({stat}))'
    # ).mark_circle(
    # ).encode(
    #     x='form5:Q',
    #     y='form3:Q'
    # ).properties(
    #     width=dims['width-pts']
    # )

    # Define lines plot [stat vs round for selected players]
    lines = base.mark_line(
        point=True
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
            title='Name'),
        tooltip=[
            alt.Tooltip(
                shorthand=f"{'cuml_stat' if cumulative else stat}:Q",
                format=' .2~s',
                title=('Cumulative ' if cumulative else '') + stat_title),
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
