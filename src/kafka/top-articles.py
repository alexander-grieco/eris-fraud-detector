import sys
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json
from webpage_info import WEBSITE_NAME, GROUP
from schema_info import key_schema_str, value_schema_str
import argparse

# loading schema to top articles
value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)

# producer class for top-articles
class ProducerAvroArticles(object):
    def __init__(self, server, schema_registry, topic):
        # define top-articles producer with avro serialization
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema,
            default_value_schema=value_schema
        )
        self.topic = topic

    # top-articles producer
    def top_produce(self):
        while True:
            # timestamp for this round of top-articles
            # uses one timestamp for each round of top-articles
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # list of top ten articles
            for i in range(10):
                #website url with random page and group
                url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,101))

                # kev,value definition
                key = {
                    "url" : url
                }
                value = {
                    "url" : url,
                    "timestamp" : timestamp
                }

                # produce top-articles to topic
                self.producer.produce(topic = self.topic, value=value, key=key)

            # produce new list of top-articles every 60 seconds
            time.sleep(60);
        print("\nFlushing records")
        self.producer.flush()


def main(args):
    # getting arguments for producer
    server = args.bootstrap_servers
    schema_registry = args.schema_registry
    topic = args.topic

    #defining producer and starting production
    p = ProducerAvroArticles(server, schema_registry, topic)
    p.top_produce()


if __name__ == '__main__':
    # argument parser to give the option of defining inputs
    parser = argparse.ArgumentParser(description="Top article producer")
    parser.add_argument('-b', dest="bootstrap_servers",
                        default="localhost:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                        default="http://localhost:8081", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="top_articles",
                        help="Topic name")

    main(parser.parse_args())
