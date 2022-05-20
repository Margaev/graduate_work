FROM python:3.9.12-buster
WORKDIR /opt/ip_packets_consumer
COPY ./ip_packets_consumer .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "ip_packets_consumer.py"]
