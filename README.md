# New-news
My Insight Data Engineering project for the NY Winter 2019 session. New-news is an application that filter's suggestions based on a user's history.

A video demo of the application can be found [here](https://www.youtube.com/watch?v=fFACYU7QMPk).

# Motivation
According to a 2014 study by Chartbeat, 55% of users are spending 15 seconds or less on each page on the websites they track (mainly online periodicals). This shows that user engagement is an incredibly hard thing to retain. One way to improve user engagement is to not display content that is stale to the user. New-news fixes this problem by tracking user activity and ensuring that any suggestions listed on each page prioritize pages the user has not visited.

# Pipeline
![alt text](img/newnews-pipeline.png)
New-news runs a pipeline on the AWS cloud, using the following cluster configurations:

* three m4.large EC2 instances for Kafka
* three m4.large EC2 instances for Cassandra
* one t2.micro EC2 instance to run the Dash front-end application
