#!/bin/bash
CLUSTER_NAME=kafka-cluster

# delete connectors
peg sshcmd-node ${CLUSTER_NAME} 1 "curl -X DELETE localhost:8083/connectors/cassandra-sink-combined"
peg sshcmd-node ${CLUSTER_NAME} 1 "curl -X DELETE localhost:8083/connectors/cassandra-sink-top"

# stop producer scripts
peg sshcmd-node ${CLUSTER_NAME} 1 "tmux kill-session -p produce"

# stop all Confluent's services
peg sshcmd-cluster ${CLUSTER_NAME} "sudo ~/confluent/bin/ksql-server-stop"
peg sshcmd-cluster ${CLUSTER_NAME} "sudo pkill -f connect" #connect doesn't have a stop command in Confluent
peg sshcmd-cluster ${CLUSTER_NAME} "sudo ~/confluent/bin/schema-registry-stop-service"
peg sshcmd-cluster ${CLUSTER_NAME} "sudo ~/confluent/bin/kafka-server-stop"
peg sshcmd-cluster ${CLUSTER_NAME} "sudo ~/confluent/bin/zookeeper-server-stop"
