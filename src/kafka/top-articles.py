import sys
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json
from webpage_info import WEBSITE_NAME, GROUP, NUM_PAGES

'''
TOP_ARTICLES PRODUCER CLASS
-- Creates an object that stores the Confluent Kafka producer as well as the schema
definition of top_articles. Has the method top_produce which does the actual producing
'''
class ProducerAvroArticles(object):
    def __init__(self, server, schema_registry, topic):
        # Key Schema definition for top articles
        self.key = avro.loads("""
        {
            "namespace": "articles",
            "name":"key",
            "type":"record",
            "fields" : [
                {"name" : "url", "type" : "string"}
            ]
        }
        """)

        # Value Schema definition for top articles
        self.value = avro.loads("""
        {
           "namespace": "articles",
           "name": "value",
           "type": "record",
           "fields" : [
                {"name" : "url", "type" : "string"},
                {"name" : "timestamp", "type" : "string"}
           ]
        }
        """)


        # define top-articles producer with avro serialization
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=self.key,
            default_value_schema=self.value
        )
        self.topic = topic

    '''
    Creates a random URL from the namespace of URLs
    -- Inputs: None
    -- Outputs: generated URL
    '''
    def getUrl(self):
        return (WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,NUM_PAGES)))

    '''
    Sets the key,value pair of the kafka record
    -- Inputs: url,timestamp
    -- Outputs: key,value pair of kafka record
    '''
    def setKV(self,url,timestamp):
        key = {"url" : url}
        value = {"url" : url, "timestamp" : timestamp}
        return (key,value)

    '''
    PRODUCE RECORD
    -- get the current time, use as timestamp for all 15 top pages
    -- loop 15 times and do the following each time:
        - Create the url by randomly selecting a subsection (i.e. GROUP) and randomly selecting
        a number for the page number within that subsection(ex: politics/page56). This is prepended
        by the name of the entire website to give a complete URL.
        - Set the key,value pair values and produce the topic to the kafka cluster
    -- Repeat every 60 seconds
    '''
    def top_produce(self):
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for i in range(15):
                # generating url
                url = self.getUrl()

                # kev,value definition
                key,value = self.setKV(url,timestamp)

                # produce top-articles to topic
                self.producer.produce(topic = self.topic, value=value, key=key)

            # produce new list of top-articles every 60 seconds
            time.sleep(60);
        print("\nFlushing records")
        self.producer.flush()


if __name__ == '__main__':
    # getting arguments for producer
    server = sys.argv[1]            # usually: localhost:9092
    schema_registry = sys.argv[2]   # usually: http://localhost:8081
    topic = sys.argv[3]             # usually: top_articles

    # loading schema to top articles
    value_schema = avro.loads(value_schema_str)
    key_schema = avro.loads(key_schema_str)

    #defining producer and starting production
    p = ProducerAvroArticles(server, schema_registry, topic)
    p.top_produce()
