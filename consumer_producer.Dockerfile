FROM python:3.9.12-buster
WORKDIR /opt/consumer_producer
COPY ./python_consumer_producer .
COPY ./data_models ./data_models
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "consumer_producer.py"]
