# Running New-news
## Loading Kafka Services
Run the following commands on your local machine:
1. ```bash peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/zookeeper-server-start ~/confluent/etc/kafka/zookeeper.properties &> ~/confluent/logs/zookeeper.out&"```
2. ```bash peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/kafka-server-start ~/confluent/etc/kafka/server.properties &> ~/confluent/logs/kafka.out&"```
3. ```bash peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/schema-registry-start  ~/confluent/etc/schema-registry/schema-registry.properties &> ~/confluent/logs/schema_registry.out&"```
4. ```bash peg sshcmd-node kafka-cluster 1 "bash ~/new-news/scripts/kafka-producer.sh 5 produce"```
5. ```bash peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/connect-distributed ~/confluent/etc/schema-registry/connect-avro-distributed.properties &> ~/confluent/logs/connect.out&"```
6. ```bash peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/ksql-server-start ~/confluent/etc/ksql/ksql-server.properties --queries-file ~/new-news/src/kafka/ksql/queries.sql &> ~/confluent/logs/ksql.out&"```


## Loading Connectors
Then, on any of your Kafka brokers, run the following two commands to load the respective connectors to transfer data from Kafka to Cassandra. Again, remember to update the input for cassandra.contact.points with your Cassandra cluster's private ips.

1. curl -X POST -H "Content-Type: application/json" --data '{  
	"name" : "cassandra-sink-combined",  
	"config" : {    
		"connector.class" : "io.confluent.connect.cassandra.CassandraSinkConnector",     
    "tasks.max" : 1,   "value.converter": "io.confluent.connect.avro.AvroConverter",    
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",    
    "value.converter.schema.registry.url": "http://localhost:8081",     
    "cassandra.contact.points" : "Private_IPs",   
    "cassandra.keyspace" : "combined_dist",   
    "topics" : "COMBINED_FINAL",    
    "cassandra.offset.storage.table" : "combined_offset"          
	}
}' http://localhost:8083/connectors

2. curl -X POST -H "Content-Type: application/json" --data '{  
	"name" : "cassandra-sink-top",  
	"config" : {    
		"connector.class" : "io.confluent.connect.cassandra.CassandraSinkConnector",    
    "tasks.max" : 1,    
    "value.converter": "io.confluent.connect.avro.AvroConverter",   
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",    
    "value.converter.schema.registry.url": "http://localhost:8081",   
    "transforms" : "createKey",   
    "transforms.createKey.fields" : "URL",    
    "transforms.createKey.type" : "org.apache.kafka.connect.transforms.ValueToKey",   
    "cassandra.contact.points" : "Private_IPs",   
    "cassandra.keyspace" : "combined_dist",   
    "topics" : "TOP_STREAM_PART",   
    "cassandra.offset.storage.table" : "top_offsets"    
  }
}' http://localhost:8083/connectors

Ensure that both connectors have been loaded properly by running the command: `curl localhost:8083/connectors`

This will list the currently active connectors. You should see something like: "[cassandra-sink-combined, cassandra-sink-top]"

## Stopping New-news
Run the command ```bash <path-to-newnews>/src/bash/kafka-stop.sh```. This will delete the connectors, stop the python scripts producing records, and will shut down all services making up Confluent Kafka. 
