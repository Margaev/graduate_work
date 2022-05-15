Prerequisites:
* Docker
* Docker-compose

To start this project use `docker-compose up -d`

To check is everything is up and running use `curl http://localhost:9200/de-enriched-data/_count`
to check if data is transmitted to elasticsearch.

Or you can run console consumer with `kafka-console-consumer.sh --bootstrap-server kafka-1:9092 --topic
[topic_name (de-source-data, de-enriched-data)] [--partition <int>]`

`/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19091,kafka-2:29091,kafka-3:39091 --topic en0_topic`

`/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19091,kafka-2:29091,kafka-3:39091 --topic en0_topic`

`sudo docker inspect --format "{{json .State.Health}}" kafka-1 | jq '.'`