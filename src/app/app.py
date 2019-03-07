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
HOST=['list of private ips for cassandra cluster']
KEYSPACE='combined_dist'
WEBSITE='https://fakenews.com/'

# Connect to Cassandra and prepare queries for later execution
session = cassandra_client.start_connection(HOST, KEYSPACE)
prep_top_query = cassandra_client.prepare_top_query(session)
prep_combined_query = cassandra_client.prepare_combined_query(session)

# Create list of emails - uses same seed at producer to get same emails
EMAILS = []
for i in range(NUM_USERS):
    faker.seed(i + 9092) # seed to ensure consistent emails
    EMAILS.append(faker.ascii_safe_email())

# CSS stylesheet included by Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__) # defining dash app
server = flask.Flask(__name__) # starting flask server

# defining cache - used to speed up performance of cassandra queries
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
TIMEOUT = 55



app.layout = html.Div(children=[
    # title and subtitle
    html.H1(children='New-News'),
    html.H2(children="Discover personalized suggestions based on user's history"),

    # dropdown that contains all users. If selected creates callback to Cassandra
    html.Div(children = [html.H4('Select Users'), dcc.Dropdown(
        id='user_email',
        options=[{'label': e, 'value': e} for e in EMAILS],
        value= [],
        multi=True,
    )], style={'width':'72%'}),

    # Top articles table that will always show up on the right side of user's screen
    html.Div(children=html.Div(id='top_articles'), className='row', style={'width':'25%', 'position':'fixed', 'top':'150px', 'right':20}),

    # area for tables when a user is selected from the dropdown shows top
    #suggestions (up to 15) and lists which websites from the current list
    #of top-websites that the user has already visited
    html.Div(children=html.Div(id='tables'), className='row', style={'width':'72%', 'margin-bottom': 100, 'margin-left':'8%'}),

    # update interval of 5 seconds - makes sure tables are updated every 5 seconds
    dcc.Interval(id='table_update', interval=5*1000, n_intervals=0),
])

# callback for user tables, gets called every time a user is selected from dropdown and every 5 seconds
@app.callback(
    dash.dependencies.Output('tables', 'children'),
    [dash.dependencies.Input('user_email', 'value'),
    dash.dependencies.Input('table_update', 'n_intervals')],)
@cache.memoize(timeout=TIMEOUT) # caches data for quick requerying
def update_combined(user_email, table_update):
    tables = []
    for e in user_email:
        # gets the current top articles in a datafram
        df1 = cassandra_client.get_top(prep_top_query, session)

        # gets website urls of any site in top articles that the user has already visited
        df2 = cassandra_client.get_combined(e, df1['url'].values.tolist(), prep_combined_query, session)

        # creates dataframe for display
        df = pd.DataFrame()
        df['Suggested'] = ""
        df["Visited"] = ""

        # if no already visited sites, set dataframe to list of top articles
        if df2.empty :
            df['Suggested'] = df1.values.tolist()

        # if visited sites, select only non-visited to put in suggested column,
        # and put already visited websites in visited column
        else:
            common = df1.merge(df2,on=['url','url'])
            df['Suggested'] = df1[(~df1.url.isin(common.url))].values.tolist()
            df['Visited'] = pd.Series(df1[(df1.url.isin(common.url))].values.tolist()).dropna()

        # create Dash datatable and append it to list of datatables
        tables.append(
            html.Div(
                children=[
                    html.H4(e), #creates title for table that is user's email
                    html.Div(dash_table.DataTable(
                        id=e,
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data = df.to_dict("rows"),
                        style_table={
                            'minWidth' : '100%',
                            'maxHeight': '150',
                            'overflowY': 'scroll',
                        },
                        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                        style_cell={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white',
                            'textAlign': 'left',
                            'width': '50%'
                        },
                    ))
                ],
                style={'padding-left':5, 'padding-right':5, 'width':'75%', 'padding-top':5, 'textAlign':'center'}
            )
        )
    return tables # return list of dash datatables to display


# creates table of top articles
@app.callback(
    dash.dependencies.Output('top_articles', 'children'),
    [dash.dependencies.Input('table_update', 'n_intervals')])
@cache.memoize(timeout=TIMEOUT) #caching data for faster performance
def update_top(table_update):
    table = []

    #gets top article information, stores in DataFrame
    df = cassandra_client.get_top(prep_top_query, session)

    # creates dash DataTable and appends it to table list
    table.append(html.Div(children=[html.H4("Top Articles"),html.Div(children=dash_table.DataTable(
        id='top',
        columns=[{"name": i, "id": i} for i in df.columns],
        data = df.to_dict("rows"),
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'textAlign': 'left',
            'width': '50%'
        },
    ))], style={'textAlign':'center'}))
    return table # returns table to display

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080)
