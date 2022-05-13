FROM python:3.9.12-buster
WORKDIR /opt/consumer_producer
COPY ./python_consumer_producer .
COPY ./data_models ./data_models
RUN pip install -r ./requirements.txt
#CMD bash add_postgres_connector.sh && bash add_es_connector.sh && python3 consumer_producer.py
CMD ["python3", "consumer_producer.py"]
