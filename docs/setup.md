# Table of Contents
1. [Setting Up New-news](README.md#setting-up-new-news)
    1. [Setting Up Clusters](README.md#setting-up-clusters)
        1. [Confluent Kafka](README.md#setting-up-confluent)
        2. [Cassandra](README.md#setting-up-cassandra)
        3. [Dash](README.md#setting-up-dash)
2. [Running New-news](README.md#running-new-news)
    1. [Loading Kafka Services](README.md#loading-kafka-services)
    2. [Loading Connectors](README.md#loading-connectors)


# Setting Up New-news

This guide makes use of Pegasus (documentation [here](https://github.com/InsightDataScience/pegasus)). The .yml files necessary to set up each individual cluster are found in ./docs/config/pegasus. Make sure to input the subnet id, PEM keypair, and security group ids for your AWS account.

## Setting up Clusters
### Setting up Confluent

Next you need to use the files list in this repository under ./docs/config/confluent and update the corresponding files on each Kafka node located in the following directories
* confluent/etc/kafka/zookeeper.properties
* confluent/etc/kafka/server.properties
* confluent/etc/schema-registry/schema-registry.properties
* confluent/etc/schema-registry/connect-avro-distributed.properties
* confluent/etc/confluent-control-center/control-center.properties
* confluent/etc/ksql/ksql-server.properties

Make sure to update any public DNS addresses or private IPs listed in these files to match the configuration of your servers

### Setting up Cassandra
On each Cassandra node, install the most recent Cassandra 3.0 download from [this](https://cassandra.apache.org/download/) page. Then, go to <path-to-Cassandra>/conf and edit the cassandra.yaml file according to the directions under the "Configure Cassandra" headline on [this](https://github.com/InsightDataScience/data-engineering-ecosystem/wiki/cassandra) page. Make sure to run the "cassandra" command to build the configuration after you are done editing the cassandra.yaml file.


### Setting up Dash
Transfer all files from the ./src/app folder into dash and then follow [this](https://www.digitalocean.com/community/tutorials/how-to-deploy-python-wsgi-apps-using-gunicorn-http-server-behind-nginx) tutorial to host the dash app on your dash server.


# Running New-news
## Loading Kafka Services
Run the following commands on your local machine where you have pegasus installed. The "nohup" command will make the services continue to run even after you log off or close your terminal session. Each nohup command also redirects its output to a log file for debugging purposes.
1. peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/zookeeper-server-start ~/confluent/etc/kafka/zookeeper.properties &> zookeeper.out&"
2. peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/kafka-server-start ~/confluent/etc/kafka/server.properties &> kafka.out&"
3. peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/schema-registry-start  ~/confluent/etc/schema-registry/schema-registry.properties &> schema_registry.out&"
4. peg sshcmd-node kafka-cluster 1 "bash ~/new-news/scripts/kafka-producer.sh [NUM INSTANCES] [SESSION NAME]" where num instances is the number of instances you want to be created, i.e. the number of producers, and session name is an arbitrary name you give to the session . This script starts the data generation. To stop data generation simply run this command: tmux kill-session -t [SESSION NAME].
5. peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/connect-distributed ~/confluent/etc/schema-registry/connect-avro-distributed.properties &> connect.out&"
6. peg sshcmd-cluster kafka-cluster "nohup sudo ~/confluent/bin/ksql-server-start ~/confluent/etc/ksql/ksql-server.properties --queries-file ~/new-news/src/kafka/ksql/queries.sql &> ksql.out&"


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

Ensure that both connectors have been loaded properly by running the command: curl localhost:8083/connectors

This will list the currently active connectors. You should see something like: "[cassandra-sink-combined, cassandra-sink-top]"
