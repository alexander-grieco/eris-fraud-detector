/* create pageview stream */
create stream pageviews_stream_test
  with (kafka_topic='pageview',
        value_format='avro',
        timestamp='timestamp',
        timestamp_format = 'yyyy-MM-dd HH:mm:ss');

/* create top_articles */
create stream top_stream_test
  with (kafka_topic='top_articles',
        value_format='avro',
        timestamp='timestamp',
        timestamp_format = 'yyyy-MM-dd HH:mm:ss');

create stream top_stream_part as
  select *, ROWTIME as top_rowtime
  from top_stream_test
  partition by url;


/* create combined stream */
create stream combined as
  select a.url as url,
          b.url as top_art_url,
          a.email as email,
          a.timestamp as pv_timestamp,
          b.ROWTIME as top_rowtime,
          (email + a.url) as key
  from pageviews_stream_test a left join top_stream_test b
    within 6 hours
  on a.url = b.url
  where b.url is not null;

/* partition by key for */
create stream combined_part as
  select *
  from combined
  partition by key;

/* select only entries where timestamp of top-articles is within last 60 seconds */
create stream combined_final as
  select url,
          email,
          top_rowtime, 
          ROWKEY as key
  from combined_part
  where ROWTIME - top_rowtime <= 60000;
