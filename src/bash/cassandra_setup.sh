#!/bin/bash
PEG_ROOT=$(dirname ${BASH_SOURCE})/../..

CLUSTER_NAME=cassandra-cluster

# starting instances
peg up ${PEG_ROOT}/docs/config/pegasus/cassandra/master.yml &
peg up ${PEG_ROOT}/docs/config/pegasus/cassandra/worker.yml &
wait
peg fetch $CLUSTER_NAME

# install necessary components
peg install ${CLUSTER_NAME} ssh
peg install ${CLUSTER_NAME} aws
peg install ${CLUSTER_NAME} environment

# install and unzip cassandra files
peg sshcmd-cluster ${CLUSTER_NAME} "curl -O http://mirrors.gigenet.com/apache/cassandra/3.0.18/apache-cassandra-3.0.18-bin.tar.gz"
peg sshcmd-cluster ${CLUSTER_NAME} "tar -zxf apache-cassandra-3.0.18-bin.tar.gz"
peg sshcmd-cluster ${CLUSTER_NAME} "mv apache-cassandra-3.0.18 cassandra"
