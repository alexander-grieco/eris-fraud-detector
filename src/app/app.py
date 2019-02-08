# -*- coding: utf-8 -*-
import dash
import dash.dependencies
import dash_core_components as dcc
import dash_html_components as html
from faker import Faker
import dash_table
import pandas as pd
from datetime import datetime
import numpy as np
import cassandra_client
from flask_caching import Cache

NUM_USERS = 5000 #number of users
faker = Faker()
HOST=['10.0.0.9']
KEYSPACE='combined'
WEBSITE='https://fakenews.com/'

session = cassandra_client.start_connection(HOST, KEYSPACE)
prep_top_query = cassandra_client.prepare_top_query(session)
prep_combined_query = cassandra_client.prepare_combined_query(session)

EMAILS = []
for i in range(NUM_USERS):
    faker.seed(i + 9092) # seed to ensure consistent emails
    EMAILS.append(faker.ascii_safe_email())


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
TIMEOUT = 60



app.layout = html.Div(children=[
    html.H1(children='New-News'),

    html.Div(children='Discover a user\'s top suggested articles.'),


    html.Label('Select User(s)'),
    dcc.Dropdown(
        id='user_email',
        options=[{'label': e, 'value': e} for e in EMAILS],
        value= [],
        multi=True
    ),
    html.Div(children=html.Div(id='top_articles'), className='row', style={'float':'right', 'width':'25%'}),
    html.Div(children=html.Div(id='tables'), className='row', style={'width':'75%', 'margin-bottom': 100}),
    dcc.Interval(id='table_update', interval=5*1000, n_intervals=0),
])


@app.callback(
    dash.dependencies.Output('tables', 'children'),
    [dash.dependencies.Input('user_email', 'value'),
    dash.dependencies.Input('table_update', 'n_intervals')],)
@cache.memoize(timeout=TIMEOUT)
def update_combined(user_email, table_update):
    tables = []
    for e in user_email:
        df2 = cassandra_client.get_combined(e, prep_combined_query, session)
        df1 = cassandra_client.get_top(prep_top_query, session)

        df = pd.DataFrame()
        df['Suggested'] = ""
        df["Visited"] = ""
        if df2.empty :
            df['Suggested'] = df1.values.tolist()

        else:
            common = df1.merge(df2,on=['url','url'])
            df['Suggested'] = df1[(~df1.url.isin(common.url))].values.tolist()
            df['Visited'] = pd.Series(df1[(df1.url.isin(common.url))].values.tolist()).dropna()

        tables.append(html.Div(children=[html.Div(e), html.Div(dash_table.DataTable(
            id=e,
            columns=[{"name": i, "id": i} for i in df.columns],
            data = df.to_dict("rows"),
            style_cell={'textAlign': 'left'},
        ))], style={'margin-left':5,'margin-right':5,'float':'left', 'margin-top':'5', 'textAlign':'center'}))
    return tables


@app.callback(
    dash.dependencies.Output('top_articles', 'children'),
    [dash.dependencies.Input('table_update', 'n_intervals')])
@cache.memoize(timeout=TIMEOUT)
def update_top(table_update):
    table = []
    df = cassandra_client.get_top(prep_top_query, session)

    table.append(html.Div(children=[html.Div("Top Articles"),html.Div(children=dash_table.DataTable(
        id='top',
        columns=[{"name": i, "id": i} for i in df.columns],
        data = df.to_dict("rows"),
        style_cell={'textAlign': 'left'},
    ))], style={'textAlign':'center'}))
    return table

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
