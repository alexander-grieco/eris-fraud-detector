import datetime
import time
import dateutil.parser
import json
import cassandra
from cassandra.cluster import Cluster
from kafka import KafkaConsumer

from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

# Define brokers for Kafka and cluster parameters for Cassandra:
broker = ['ec2-3-82-184-126.compute-1.amazonaws.com']
topic = 'pageview'
keyspace = 'test_pageviews'
cassandra_host_names = ['ec2-3-92-115-89.compute-1.amazonaws.com']

# create the consumer
c = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'groupid',
    'schema.registry.url': 'http://localhost:8081'})

c.subscribe(['pageview_test'])
print('Consumer created')

# create the Cassandra configuration
cluster = Cluster(cassandra_host_names)
session = cluster.connect(keyspace)
print('Connected to Cassandra')
insert_prep = session.prepare("""
    insert into test (
    transaction_id,
    timestamp,
    url,
    user_id)
    VALUES (?, ?, ?, ?)""")




while True:
    try:
        msg = c.poll(1)
        if msg is None:
            continue

        if msg.error():
            continue

        line = msg.value()
        values = []
        values.append(line['pageview_id'])
        values.append(line['timestamp'])
        values.append(line['url'])
        values.append(line['user_id'])
        session.execute(insert_prep, values)
        print('Message inserted into Cassandra')

        print(msg.value())





    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break
    except KeyboardInterrupt:
        break


c.close()
