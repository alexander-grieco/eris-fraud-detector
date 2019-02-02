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


NUM_USERS = 500
PV_TOPIC = 'pageview'

value_schema_pv = avro.loads(value_schema_pv_str)
key_schema_pv = avro.loads(key_schema_pv_str)


class ProducerAvroPV(object):

    def __init__(self, server, schema_registry, topic, users):
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema_pv,
            default_value_schema=value_schema_pv
        )
        self.topic = topic
        self.users = users

    def pv_produce(self):
        while True:
            user_id = numpy.random.choice(self.users)['mail']
            url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,101))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pageview_id = str(uuid.uuid4())

            key = {"pageview_id" : pageview_id}
            value = {
                "user_id": user_id,
                "url" : url,
                "timestamp" : timestamp,
                "pageview_id" : pageview_id
            }

            self.producer.produce(topic = self.topic, value=value, key=key)
            time.sleep(0.5);
            print("record created:" + json.dumps(value))
        print("\nFlushing records")
        self.producer.flush()


#if __name__ == "__main__":
def main(args):
    #server = str(sys.argv[1])
    #schema_registry = str(sys.argv[2])
    server = args.bootstrap_servers
    schema_registry = args.schema_registry
    topic = args.topic

    faker = Faker()

    users = []
    for i in range(NUM_USERS):
        faker.seed((i+9092)*32)
        users.append(faker.simple_profile())

    p = ProducerAvroPV(server, schema_registry, topic, users)
    p.pv_produce()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for handling Avro data")
    parser.add_argument('-b', dest="bootstrap_servers",
                        default="localhost:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                        default="http://localhost:8081", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="pageview",
                        help="Topic name")

    main(parser.parse_args())
