# Internet Traffic Monitoring System
## Proposed architecture diagram
<img width="1026" alt="image" src="https://user-images.githubusercontent.com/49162274/170590210-85342567-73f1-4fa8-be0d-67a1ef659ffb.png">

## Prerequisites:
* Docker
* Docker-compose

To start this project use `docker-compose up -d`

## Sample interface:
![telegram-cloud-photo-size-2-5213212002758015927-y](https://user-images.githubusercontent.com/49162274/170590275-505e635f-1b70-4adf-aed9-aed08f3db5e3.jpg)


## Console consumer and producer
`docker exec -it kafka-1 bash`

`/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19091,kafka-2:29091,kafka-3:39091 --topic en0_topic`

`/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19091,kafka-2:29091,kafka-3:39091 --topic en0_topic`
