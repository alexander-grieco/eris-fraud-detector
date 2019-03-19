#Setting Up New-news
This guide makes use of Pegasus (documentation [here](https://github.com/InsightDataScience/pegasus)). The .yml files necessary to set up each individual cluster are found in <path to project>/docs/config/pegasus. Make sure to input the subnet id, PEM keypair, and security group ids for your AWS account in each configuration file.

## Setting up Clusters
### Setting up Confluent
Run the command `bash <path to project>/src/bash/kafka_setup.sh` to set up kafka cluster.

After that is complete, you need to use the files list in this repository under <path to project>/docs/config/confluent and update the corresponding files on each Kafka node located in the following directories
* confluent/etc/kafka/zookeeper.properties
* confluent/etc/kafka/server.properties
* confluent/etc/schema-registry/connect-avro-distributed.properties
* confluent/etc/confluent-control-center/control-center.properties
* confluent/etc/ksql/ksql-server.properties

**Make sure to update any public DNS addresses or private IPs listed in these files to match the configuration of your servers**

Further, make sure to move this repository to each node in your Kafka cluster.

### Setting up Cassandra
To set up Cassandra, run the command `bash <path-to-project>/src/bash/cassandra_setup.sh`

Next you have to configure the cluster. You can do this in whichever way you like, or you can follow the directions under the "Configure Cassandra" headline on [this](https://github.com/InsightDataScience/data-engineering-ecosystem/wiki/cassandra) page. Make sure to run the "cassandra" command to build the configuration after you are done editing the cassandra.yaml file.


### Setting up Dash
To set up Dash, run the command `bash <path-to-project>/src/bash/dash-setup.sh`

You can host this app in any way you like, but I followed the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-deploy-python-wsgi-apps-using-gunicorn-http-server-behind-nginx). Note that you should wait until New-news is running to start the application.
