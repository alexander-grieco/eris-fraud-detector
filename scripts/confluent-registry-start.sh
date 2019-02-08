#!/bin/bash

#peg sshcmd-cluster kafka-cluster "~/confluent/bin/zookeeper-server-start ~/confluent/etc/kafka/zookeeper.properties"
#peg sshcmd-cluster kafka-cluster "~/confluent/bin/kafka-server-start ~/confluent/etc/kafka/server.properties"


#################################################################################
# MAKE SURE TO START KAFKA BEFORE AND CREATE TOPICS FOR PAGEVIEWS AND ARTICLES  #
#################################################################################

peg sshcmd-cluster kafka-cluster "~/confluent/bin/schema-registry-start ~/confluent/etc/schema-registry/schema-registry.properties"
