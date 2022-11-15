import altair as alt
import json

from bs4 import BeautifulSoup
from dash_bootstrap_components.themes import SLATE

from get_data import get_data


# Configure altair
alt.data_transformers.disable_max_rows()

# Get data
if False: # if debugging
    import pickle
    with open('./data.pkl', 'rb') as f: df = pickle.load(f)['players-df']
else:
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

# Concatenate charts
charts = alt.vconcat(
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

# Get chart HTML and edit
soup = BeautifulSoup(charts.to_html(), 'html.parser')

## add page title
soup.html.head.append(soup.new_tag('title'))
soup.html.head.title.string = 'Fantasy EPL Dashboard'

## add CSS
soup.html.head.append(soup.new_tag('link', rel='stylesheet', href=SLATE))

## edit chart javascript
js = json.loads(charts.to_json())
js_tag = lambda s: f'JS_TAG{"{"}{s}{"}"}JS_TAG'
st_tag = lambda s: f'ST_TAG{"{"}{s}{"}"}ST_TAG'

### edit chart dimensions to be adaptive
js['vconcat'][0]['width'] = js_tag('0.215*window.innerWidth')
js['vconcat'][0]['height'] = js_tag('0.37*window.innerHeight')
js['vconcat'][1]['width'] = js_tag('0.9*window.innerWidth')
js['vconcat'][1]['height'] = js_tag('0.37*window.innerHeight')

### get lines y field from dropdown
js['vconcat'][1]['encoding']['y']['field'] = \
    js_tag(f'document.getElementById({st_tag("lns-type")}).value')
js['vconcat'][1]['encoding']['y']['scale']['domain'] = [
    0,
    js_tag(f'((document.getElementById({st_tag("lns-type")}).value == '
        f'{st_tag("cumulative")}) ? '
        f'{df.groupby("name").sum()["total_points"].max()} : '
        f'{df["total_points"].max()})')
]

### convert json to string and remove tags
js = json.dumps(
    js
).replace(
    '"JS_TAG{',
    ''
).replace(
    '}JS_TAG"',
    ''
).replace(
    'ST_TAG{',
    '"'
).replace(
    '}ST_TAG',
    '"'
)

### overwrite javascript in html and move to head
i = soup.html.body.script.string.find('{"config')
j = soup.html.body.script.string.find(';')
soup.html.head.append(soup.new_tag('script'))
soup.html.head.find_all('script')[-1].string = (
    'function get_chart() {'
    + soup.html.body.script.string[:i]
    + js
    + soup.html.body.script.string[j:]
    + '};')
soup.html.body.script.decompose()

## add dropdown menu and script to update chart
soup.html.body['onload'] = 'get_chart()'
soup.html.body.append(
    soup.new_tag('select', id='lns-type', onchange='get_chart()'))
for v, s in {
    'total_points': 'Weekly', 'cumulative': 'Cumulative', 'form': 'Form'
}.items():
    soup.html.body.find('select').append(soup.new_tag('option', value=v))
    soup.html.body.find('select').find_all('option')[-1].string = s

# Write HTML to file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
