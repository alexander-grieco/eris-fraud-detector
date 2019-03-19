#!/bin/bash
PEG_ROOT=$(dirname ${BASH_SOURCE})/../..

CLUSTER_NAME=dash-cluster

# starting instance on AWS
peg up ${PEG_ROOT}/docs/config/pegasus/dash/master.yml &
wait
peg fetch $CLUSTER_NAME

# install necessary components
peg install ${CLUSTER_NAME} ssh
peg install ${CLUSTER_NAME} aws
peg install ${CLUSTER_NAME} environment


# install dash-app dependencies
peg sshcmd-cluster ${CLUSTER_NAME} "pip install dash==0.39.0"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install dash-html-components==0.14.0"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install dash-core-components==0.44.0"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install dash-table==3.6.0"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install dash-daq==0.1.0"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install faker"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install pandas"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install numpy"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install cassandra-driver"
peg sshcmd-cluster ${CLUSTER_NAME} "pip install Flask-Caching"
