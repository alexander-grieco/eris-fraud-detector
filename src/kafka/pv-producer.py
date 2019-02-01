import sys
from faker import Faker
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json


NUM_USERS = 500
PV_TOPIC = 'pageview'
WEBSITE_NAME = 'https://fakenews.com/'
GROUP = ['politics/'] #, 'sports/', 'international/', 'business/',
            #'tech/', 'arts/', 'health/','science/', 'social/', 'opinion/']

# Key Schema definition for a pageview
key_schema_pv_str = """
{
    "namespace": "pageview",
    "name":"key",
    "type":"record",
    "fields" : [
        {"name" : "pageview_id", "type" : "string"}
    ]
}
"""

# Value Schema definition for a pageview
value_schema_pv_str = """
{
   "namespace": "pageview",
   "name": "value",
   "type": "record",
   "fields" : [
        {"name" : "user_id", "type" : "string"},
        {"name" : "url", "type" : "string"},
        {"name" : "timestamp", "type" : "string"},
        {"name" : "pageview_id", "type" : "string"}
   ]
}
"""

#
value_schema_pv = avro.loads(value_schema_pv_str)
key_schema_pv = avro.loads(key_schema_pv_str)


class ProducerAvroPV(object):

    def __init__(self, server, schema_registry):
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema_pv,
            default_value_schema=value_schema_pv
        )

    def pv_produce(self):
        while True:
            user_id = numpy.random.choice(users)['mail']
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

            self.producer.produce(topic = PV_TOPIC, value=value, key=key)
            time.sleep(0.5);
            print("record created:" + json.dumps(value))
        print("\nFlushing records")
        self.producer.flush()


if __name__ == "__main__":
    server = str(sys.argv[1])
    schema_registry = str(sys.argv[2])
    faker = Faker()

    users = []
    for i in range(NUM_USERS):
        faker.seed((i+9092)*32)
        users.append(faker.simple_profile())

    p = ProducerAvroPV(server, schema_registry)
    p.pv_produce()
