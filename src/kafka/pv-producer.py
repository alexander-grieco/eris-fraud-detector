import sys
from faker import Faker
from datetime import datetime
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import uuid
import numpy

TOPIC = 'pageview-test' #change to pageview later
WEBSITE_NAME = 'https://fakenews.com/'
GROUP = ['politics/', 'sports/', 'international/', 'business/',
            'tech/', 'arts/', 'health/','science/', 'social/', 'opinion/']

# Key Schema definition for a pageview
key_schema_str = """
{
    "namespace": "test",
    "name":"key",
    "type":"record",
    "fields" : [
        {"name" : "pageview_id", "type" : "string"}
    ]
}
"""

# Value Schema definition for a pageview
value_schema_str = """
{
   "namespace": "test",
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
value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)


class ProducerAvro(object):

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
            user_id = numpy.random.choice(user_ids)
            url = WEBSITE_NAME + numpy.random.choice(GROUP) + \
                    "page" + str(numpy.random.randint(1,101))
            timestamp = datetime.now() #.strftime("%Y-%m-%d %H:%M:%S")
            pageview_id = uuid.uuid4()

            key = {"pageview_id" : pageview_id}
            value = {
                "user_id": user_id,
                "url" : url,
                "timestamp" : timestamp,
                "pageview_id" : pageview_id
            }

            self.producer.produce(topic = TOPIC, value=value, key=key)


        print("\nFlushing records")
        self.flush()





if __name__ == "__main__":
    server = str(sys.argv[1])
    schema_registry = str(sys.argv[2])
    faker = Faker()
    user_ids = [faker.free_email() for _ in range(500)]


    p = ProducerAvro(server, schema_registry)
    p.pv_produce()
