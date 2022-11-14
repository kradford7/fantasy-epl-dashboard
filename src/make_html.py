import altair as alt

from bs4 import BeautifulSoup
from dash_bootstrap_components.themes import SLATE

from get_data import get_data


# Configure altair
alt.data_transformers.disable_max_rows()

# Get data
df = get_data()['players-df']

# Define the base upon which to build plots
selector = alt.selection_multi(empty='none', fields=['name', 'position'])
base = alt.Chart(df).add_selection(selector)

# Define points plot [var(stat) vs sum(stat) facet by position]
points = base.transform_aggregate(
    var='variance(total_points)',
    sum='sum(total_points)',
    latest='argmax(round)',
    groupby=['name', 'position']
).transform_calculate(
    value='datum.sum / datum.latest.cost'
).mark_circle(
).encode(
    x=alt.X(
        shorthand='sum:Q',
        axis=alt.Axis(format=' .2~s'),
        title='Total Points'),
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
            title='Total Points'),
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
)

# Define lines plot [stat vs round for selected players]
lines = base.mark_line(
    point=True
).transform_window(
    cumulative='sum(total_points)',
    groupby=['name', 'position']
).transform_window(
    form='mean(total_points)',
    groupby=['name', 'position'],
    sort=[alt.SortField(field='round', order='descending')]
).encode(
    x=alt.X(
        shorthand='round:Q',
        axis=alt.Axis(tickMinStep=1),
        scale=alt.Scale(domain=(1, df['round'].max())),
        title='Matchday'),
    y=alt.Y(
        shorthand="total_points:Q",
        axis=alt.Axis(format=' .2~s'),
        scale=alt.Scale(domain=(0, df['total_points'].max())),
        title='Total Points'),
    color=alt.Color(
        shorthand='name:N',
        title='Name'),
    tooltip=[
        alt.Tooltip(
            shorthand='total_points:Q',
            format=' .2~s',
            title='Total Points'),
        alt.Tooltip(
            shorthand='minutes',
            title='Minutes')]
).transform_filter(
    selector
)

# Concatenate charts and publish to HTML
html = alt.vconcat(
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
).to_html()


# Edit HTML
soup = BeautifulSoup(html, 'html.parser')

## add page title
title = soup.new_tag('title')
title.string = 'Fantasy EPL Dashboard'
soup.html.head.append(title)

## add CSS
css = soup.new_tag('link', rel='stylesheet', href=SLATE)
soup.html.head.append(css)

## edit chart dimensions to be adaptive
js = soup.html.body.script.string
i = js.find('"mark": "circle"')
js = (
    js[:i]
    + '"width": 0.215*window.innerWidth, "height": 0.4*window.innerHeight, '
    + js[i:])

i = js.find('"mark": {')
soup.html.body.script.string = (
    js[:i]
    + '"width": 0.9*window.innerWidth, "height": 0.4*window.innerHeight, '
    + js[i:])

# Write HTML to file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
