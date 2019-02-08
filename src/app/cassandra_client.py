
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra import ReadTimeout
import pandas as pd
import time
import datetime

def start_connection(host, keyspace):
    cluster = Cluster(host)
    session = cluster.connect(keyspace)
    session.row_factory = dict_factory
    return session

def prepare_top_query(session):
	query = "select url from top_stream_part where top_rowtime>=? allow filtering"
	return session.prepare(query)

# def prepare_combined_query(session):
#     query = "select url from combined_real where email=? allow filtering"
#     return session.prepare(query)

def prepare_combined_query(session):
    query = "select url from combined_real where key=? allow filtering"
    return session.prepare(query)

# def get_combined(email, prepared_query, session):
#     count = session.execute_async(prepared_query, [email])
#     try:
#         rows = count.result()
#         df = pd.DataFrame(list(rows))
#     except ReadTimeout:
#         log.exception("get_combined query timed out:")
#     return df

def get_combined(email, top, prepared_query, session):
    count_final = []

    try:
        for website in top:
            key = email + str(website)
            count = list(session.execute_async(prepared_query, [key]).result())
            if len(count) != 0:
                count_final.append(count[0])
        df = pd.DataFrame(count_final)
    except ReadTimeout:
        log.exception("get_combined query timed out:")
    return df



def get_top(prepared_query, session):
    time_range = int(time.time())*1000 - 60000
    count = session.execute_async(prepared_query, [time_range])
    try:
        rows = count.result()
        df = pd.DataFrame(list(rows))
    except ReadTimeout:
        log.exception("get_top query timed out")
    return df
