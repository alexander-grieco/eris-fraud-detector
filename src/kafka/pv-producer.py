import sys
from faker import Faker
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json
from webpage_info import WEBSITE_NAME, GROUP, NUM_USERS,NUM_PAGES
import argparse


'''
PAGEVIEW PRODUCER CLASS
-- Creates an object that stores the Confluent Kafka producer as well as the schema
definition of the pageview. Has the method pv_produce which does the actual producing
'''
class ProducerAvroPV(object):

    def __init__(self, server, schema_registry, topic, emails):
        # key schema definition for a pageview
        self.key = avro.loads("""
        {
            "namespace": "pageview",
            "name":"key",
            "type":"record",
            "fields" : [
                {"name" : "pageview_id", "type" : "string"}
            ]
        }
        """)

        # Value Schema definition for a pageview
        self.value = avro.loads("""
        {
           "namespace": "pageview",
           "name": "value",
           "type": "record",
           "fields" : [
                {"name" : "email", "type" : "string"},
                {"name" : "url", "type" : "string"},
                {"name" : "timestamp", "type" : "string"},
                {"name" : "pageview_id", "type" : "string"}
           ]
        }
        """)

        # define pageview producer with avro serialization
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=self.key,
            default_value_schema=self.value
        )
        self.topic = topic
        self.emails = emails

    '''
    PRODUCE RECORD
    -- Select a random user from list of emails
    -- Create the page they are 'visiting' by randomly selecting a subsection (i.e. GROUP) and
    randomly selecting a number for the page number within that subsection(ex: politics/page56).
    This is prepended by the name of the entire website to give a complete URL.
    -- Further get the current time and generate a unique pageview id.
    -- Finally set the key,value pair values and produce the topic to the kafka cluster
    '''
    def pv_produce(self):
        while True:
            # initializing information
            email = numpy.random.choice(self.emails)
            url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,NUM_PAGES))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pageview_id = str(uuid.uuid4())

            # setting key,value pair
            key = {"pageview_id" : pageview_id}
            value = {
                "email": email,
                "url" : url,
                "timestamp" : timestamp,
                "pageview_id" : pageview_id
            }

            # producing entry to topic
            self.producer.produce(topic = self.topic, value=value, key=key)
            time.sleep(0.001);

        print("\nFlushing records")
        self.producer.flush()


if __name__ == '__main__':
    # getting arguments for producer
    server = sys.argv[1]            # usually: localhost:9092
    schema_registry = sys.argv[2]   # usually: http://localhost:8081
    topic = sys.argv[3]             # usually: pageview

    # creating list of emails
    faker = Faker()
    emails = []
    for i in range(NUM_USERS):
        faker.seed(i + 9092) # seed to ensure consistent emails
        emails.append(faker.ascii_safe_email())

    # create producer and begin producing to kafka cluster
    p = ProducerAvroPV(server, schema_registry, topic, emails)
    p.pv_produce()
