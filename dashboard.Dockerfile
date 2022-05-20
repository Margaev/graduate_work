FROM python:3.9.12-buster
WORKDIR /opt/consumer_producer
COPY ./monitoring_dashboard .
COPY ./data_models ./data_models
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
EXPOSE 8050
CMD ["python3", "dashboard.py"]
