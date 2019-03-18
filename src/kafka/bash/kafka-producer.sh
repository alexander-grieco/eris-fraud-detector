#!/bin/bash
NUM_SPAWNS=$1
SESSION=$2
tmux new-session -s $SESSION -n bash -d

# create several producers for pageviews
for ID in `seq 1 $NUM_SPAWNS`;
do
    echo $ID
    tmux new-window -t $ID
    tmux send-keys -t $SESSION:$ID "python ~/new-news/src/kafka/pv-producer.py 'localhost:9092' 'http://localhost:8081' 'pageview'"  C-m
done

# only one producer for top-articles (only want one)
for ID in `seq $((NUM_SPAWNS+1)) $((NUM_SPAWNS+1))`;
do
    echo $ID
    tmux new-window -t $ID
    tmux send-keys -t $SESSION:$ID "python ~/new-news/src/kafka/top-articles.py 'localhost:9092' 'http://localhost:8081' 'top_articles'" C-m
done
