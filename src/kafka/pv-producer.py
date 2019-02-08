import sys
from faker import Faker
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json
from webpage_info import WEBSITE_NAME, GROUP
from schema_info import key_schema_pv_str, value_schema_pv_str
import argparse

# configuartions for producer
NUM_USERS = 5000
PV_TOPIC = 'pageview'

# loading the schema from schema definitions
value_schema_pv = avro.loads(value_schema_pv_str)
key_schema_pv = avro.loads(key_schema_pv_str)


# Producer for pageviews
class ProducerAvroPV(object):

    def __init__(self, server, schema_registry, topic, emails):
        # define pageview producer with avro serialization
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema_pv,
            default_value_schema=value_schema_pv
        )
        self.topic = topic #topic to produce to
        self.emails = emails

    # pageview producer
    def pv_produce(self):
        while True:
            # email list of users
            email = numpy.random.choice(self.emails)

            #website url with random page and group
            url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,101))

            #timestamp of pageview
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # universally unique id for pageview
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
            time.sleep(0.01);

        print("\nFlushing records")
        self.producer.flush()


def main(args):
    # getting arguments for producer
    server = args.bootstrap_servers
    schema_registry = args.schema_registry
    topic = args.topic
    instance = args.instance

    # creating fake list of emails
    faker = Faker()
    emails = []
    for i in range(NUM_USERS):
        faker.seed((i+9092)*instance) # seed to ensure consistent emails
        emails.append(faker.ascii_safe_email())

    # defining producer and beginning production
    p = ProducerAvroPV(server, schema_registry, topic, emails)
    p.pv_produce()


if __name__ == '__main__':
    # argument parser to give the option of defining inputs
    parser = argparse.ArgumentParser(description="Pageview producer")
    parser.add_argument('-b', dest="bootstrap_servers",
                        default="localhost:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                        default="http://localhost:8081", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="pageview",
                        help="Topic name")
    parser.add_argument('-i', dest="instance", default=1,
                        help="number of the tmux machine that is performing the query")

    main(parser.parse_args())
