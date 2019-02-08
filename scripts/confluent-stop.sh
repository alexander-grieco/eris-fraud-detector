#!/bin/bash

# peg sshcmd-cluster kafka-cluster "~/confluent/bin/kafka-server-stop"
# peg sshcmd-cluster kafka-cluster "~/confluent/bin/zookeeper-server-stop"
# peg sshcmd-cluster kafka-cluster "sudo rm -rf /tmp/kafka-logs"
# peg sshcmd-cluster kafka-cluster "sudo rm -rf /tmp/zookeeper"

peg sshcmd-cluster kafka-cluster "~/confluent/bin/ksql-server-stop"
#peg sshcmd-cluster kafka-cluster "~/confluent/bin/schema-registry-stop"
