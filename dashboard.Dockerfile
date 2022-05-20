FROM python:3.9.12-buster
WORKDIR /opt/monitoring_dashboard
COPY ./monitoring_dashboard .
COPY ./helpers ./helpers
RUN pip install -r ./requirements.txt
EXPOSE 8050
CMD ["python3", "dashboard.py"]
