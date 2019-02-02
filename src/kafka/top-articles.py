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


value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)

class ProducerAvroArticles(object):

    def __init__(self, server, schema_registry, topic):
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema,
            default_value_schema=value_schema
        )
        self.topic = topic

    def pv_produce(self):
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for i in range(15):
                url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,101))
                key = {
                    "url" : url
                }
                value = {
                    "url" : url,
                    "timestamp" : timestamp
                }

                self.producer.produce(topic = self.topic, value=value, key=key)
                print("Record value: " + json.dumps(value))
            time.sleep(3);
        print("\nFlushing records")
        self.producer.flush()


def main(args):
    server = args.bootstrap_servers
    schema_registry = args.schema_registry
    topic = args.topic

    p = ProducerAvroArticles(server, schema_registry, topic)
    p.pv_produce()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for handling Avro data")
    parser.add_argument('-b', dest="bootstrap_servers",
                        default="localhost:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                        default="http://localhost:8081", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="top_articles",
                        help="Topic name")

    main(parser.parse_args())
