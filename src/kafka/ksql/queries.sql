/**** create pageview stream  ****/
create stream pageviews_stream_test with (kafka_topic='pageview', value_format='avro', timestamp='timestamp', timestamp_format = 'yyyy-MM-dd HH:mm:ss');
create stream pv_part as select * from pageviews_stream_test partition by url;


/**** create top_articles ****/
create stream top_stream_test with (kafka_topic='top_articles', value_format='avro', timestamp='timestamp', timestamp_format = 'yyyy-MM-dd HH:mm:ss');
create stream top_stream_part as select * from top_stream_test partition by url;
create table top_articles with (kafka_topic='TOP_STREAM_PART', value_format='avro', timestamp='timestamp', timestamp_format = 'yyyy-MM-dd HH:mm:ss', key='url');



/**** create combined ****/
create stream combined as select a.url as pv_url, b.url as top_art_url, a.email as email, a.timestamp as pv_timestamp, b.ROWTIME as top_rowtime from pv_part a left join top_articles b on a.url = b.url where b.url is not null;
create stream combined_real as select pv_url, email, top_rowtime from combined where ROWTIME - top_rowtime <= 30000;
