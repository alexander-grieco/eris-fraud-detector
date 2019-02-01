import sys
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy
import time
import json


PV_TOPIC = 'top_articles'
WEBSITE_NAME = 'https://fakenews.com/'
GROUP = ['politics/'] #, 'sports/', 'international/', 'business/',
            #'tech/', 'arts/', 'health/','science/', 'social/', 'opinion/']

# Key Schema definition for a pageview
key_schema_str = """
{
    "namespace": "articles",
    "name":"key",
    "type":"record",
    "fields" : [
        {"name" : "url", "type" : "string"}
    ]
}
"""

# Value Schema definition for a pageview
value_schema_str = """
{
   "namespace": "articles",
   "name": "value",
   "type": "record",
   "fields" : [
        {"name" : "url", "type" : "string"},
        {"name" : "timestamp", "type" : "string"}
   ]
}
"""


value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)

class ProducerAvroArticles(object):

    def __init__(self, server, schema_registry):
        self.producer = AvroProducer(
            {
                'bootstrap.servers': server,
                'schema.registry.url': schema_registry
            },
            default_key_schema=key_schema,
            default_value_schema=value_schema
        )

    def pv_produce(self):
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for i in range(15):
                url = WEBSITE_NAME + numpy.random.choice(GROUP) + "page" + str(numpy.random.randint(1,1001))
                key = {
                    "url" : url
                }
                value = {
                    "url" : url,
                    "timestamp" : timestamp
                }

                self.producer.produce(topic = PV_TOPIC, value=value, key=key)
                print("Record value: " + json.dumps(value))
            time.sleep(30);
        print("\nFlushing records")
        self.producer.flush()


if __name__ == "__main__":
    server = str(sys.argv[1])
    schema_registry = str(sys.argv[2])

    p = ProducerAvroArticles(server, schema_registry)
    p.pv_produce()
