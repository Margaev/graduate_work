FROM python:3.9.12-buster
WORKDIR /opt/http_packets_consumer
COPY ./http_packets_consumer .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "http_packets_consumer.py"]
