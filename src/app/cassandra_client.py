
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra import ReadTimeout
import pandas as pd
import time
import datetime

# initiates Cassandra session
def start_connection(host, keyspace):
    cluster = Cluster(host)
    session = cluster.connect(keyspace)
    session.row_factory = dict_factory
    return session

# prepares the top articles query for later use
def prepare_top_query(session):
	query = "select url from top_stream_part where top_rowtime>=? allow filtering"
	return session.prepare(query)

# prepares the combined query for later use
def prepare_combined_query(session):
    query = "select url from combined_real where key=?" # don't need 'allow filtering' because key is table key
    return session.prepare(query)

# peform the get combined query
def get_combined(email, top, prepared_query, session):
    count_final = []
    try:
        for website in top:
            key = email + str(website) # create key variable for quicker querying
            count = list(session.execute_async(prepared_query, [key]).result()) #get list of results

            # if there exist results, append to list
            if len(count) != 0:
                count_final.append(count[0])

        #create dataframe of results
        # This is a list of urls that the user has visited, that are currently in the top articles list
        df = pd.DataFrame(count_final)
    except ReadTimeout:
        log.exception("get_combined query timed out:")
    return df


# perform the get top articles query
def get_top(prepared_query, session):
    # only select options from last 60 seconds
    time_range = int(time.time())*1000 - 60000
    count = session.execute_async(prepared_query, [time_range])
    try:
        rows = count.result()

        # create dataframe of results
        # this is a list of urls that is the current list of top articles
        df = pd.DataFrame(list(rows))
    except ReadTimeout:
        log.exception("get_top query timed out")
    return df
