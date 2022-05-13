FROM python:3.9.12-buster
WORKDIR /opt/traffic_sniffer
COPY ./traffic_sniffer .
COPY ./data_models ./data_models
RUN pip install -r ./requirements.txt
CMD ["python3", "traffic_sniffer.py"]
