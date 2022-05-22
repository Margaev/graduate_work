FROM python:3.9.12-buster
WORKDIR /opt/raw_packets_consumer
COPY raw_packets_consumer .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "raw_packets_consumer.py"]
