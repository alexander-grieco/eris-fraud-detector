#!/bin/bash
ROOT=$(dirname ${BASH_SOURCE})/../..

CLUSTER_NAME=kafka-cluster

# starting instances
peg up ${ROOT}/docs/config/pegasus/kafka/master.yml &
peg up ${ROOT}/docs/config/pegasus/kafka/worker.yml &
wait
peg fetch $CLUSTER_NAME

# install necessary components
peg install ${CLUSTER_NAME} ssh
peg install ${CLUSTER_NAME} aws
peg install ${CLUSTER_NAME} environment

# install and unzip confluent kafka files
peg sshcmd-cluster ${CLUSTER_NAME} "curl -O http://packages.confluent.io/archive/5.1/confluent-5.1.1-2.11.tar.gz"
peg sshcmd-cluster ${CLUSTER_NAME} "tar -zxf confluent-5.1.1-2.11.tar.gz"
peg sshcmd-cluster ${CLUSTER_NAME} "mv confluent-5.1.1 confluent"

# install python libraries
peg sshcmd-cluster ${CLUSTER_NAME} "pip install faker"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install confluent_kafka"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install confluent_kafka[avro]"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install uuid"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install numpy"
