FROM python:3.9.12-buster
WORKDIR /opt/dns_packets_consumer
COPY ./dns_packets_consumer .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
CMD ["python3", "dns_packets_consumer.py"]
