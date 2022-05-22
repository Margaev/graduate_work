FROM python:3.9.12-buster
WORKDIR /opt/tcp_packets_consumer
COPY ./tcp_packets_consumer .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "tcp_packets_consumer.py"]
