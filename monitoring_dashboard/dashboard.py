import logging
import os
import datetime

import dash
import numpy as np
import plotly
import plotly.subplots
import plotly.express
from dash.dependencies import Input, Output
from dash import dcc, html

from helpers.mongo import MongoManager

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
IP_PACKETS_COLLECTION = os.environ.get("IP_PACKETS_COLLECTION", "ip_packets")
TCP_PACKETS_COLLECTION = os.environ.get("TCP_PACKETS_COLLECTION", "tcp_packets")
DNS_PACKETS_COLLECTION = os.environ.get("DNS_PACKETS_COLLECTION", "dns_packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

ip_mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=IP_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)
tcp_mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=TCP_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)
dns_mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=DNS_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)

ONE_MINUTE_IN_SECONDS = 60

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
colors = {
    "background": "#111111",
    "text": "#7FDBFF"
}

HEADING = html.Div(
    html.H2(
        children="Network Packets Monitoring Dashboard",
        style={
            "textAlign": "center",
            "color": colors["text"]
        }
    ),
)

IP_PACKETS_PER_MINUTE = html.Div(
    [
        html.H3(
            children="IP Packets per Minute",
            style={
                "textAlign": "center",
                "color": colors["text"]
            }
        ),
        dcc.Graph(id="ip-packets-per-minute"),
    ]
)

SYN_ACK_RATE_PER_MINUTE = html.Div(
    [
        html.H3(
            children="SYN/ACK Rate per Minute",
            style={
                "textAlign": "center",
                "color": colors["text"]
            }
        ),
        dcc.Graph(id="syn-ack-rate-per-minute"),
    ]
)

DNS_PACKETS_PER_MINUTE = html.Div(
    [
        html.H3(
            children="DNS Packets per Minute",
            style={
                "textAlign": "center",
                "color": colors["text"]
            }
        ),
        dcc.Graph(id="dns-packets-per-minute"),
    ]
)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    [
        HEADING,
        IP_PACKETS_PER_MINUTE,
        SYN_ACK_RATE_PER_MINUTE,
        DNS_PACKETS_PER_MINUTE,
        dcc.Interval(
            id="interval-component",
            interval=3 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]
)


@app.callback(Output("ip-packets-per-minute", "figure"),
              Input("interval-component", "n_intervals"))
def update_ip_graph_live(n):
    time_frame = 60

    end_time = int(datetime.datetime.now().replace(second=0).timestamp())
    start_time = int(end_time - datetime.timedelta(minutes=time_frame).total_seconds())
    timestamp_range = list(
        range(start_time + ONE_MINUTE_IN_SECONDS, end_time + ONE_MINUTE_IN_SECONDS, ONE_MINUTE_IN_SECONDS)
    )
    datetime_range = list(map(
        lambda timestamp: datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d %H:%M"),
        timestamp_range,
    ))

    data = {
        "minutes": list(range(1, time_frame + 1)),
        "x_labels": datetime_range,
    }

    ip_packets_count_list = ip_mongo_manager.find_packets_count_per_minute(start_time, end_time)
    ip_packets_count = {doc["timestamp"]: doc["packets_count"] for doc in ip_packets_count_list}
    data["packets"] = [ip_packets_count.get(timestamp, 0) for timestamp in timestamp_range]

    data["median"] = (ip_mongo_manager.get_median_ip_packets_count_per_minute(start_time, end_time), ) * time_frame

    fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.2)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["packets"],
        "name": "IP Packets per Minute",
        "type": "bar"
    }, 1, 1)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["median"],
        "name": "Normal Packets Trend",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines",
    }, 1, 1)

    # layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=data["minutes"],
            ticktext=data["x_labels"],
        ),
        font_size=10
    )
    fig["layout"]["margin"] = {
        "l": 0, "r": 0, "b": 0, "t": 0
    }
    fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

    return fig


@app.callback(Output("syn-ack-rate-per-minute", "figure"),
              Input("interval-component", "n_intervals"))
def update_tcp_graph_live(n):
    time_frame = 60

    end_time = int(datetime.datetime.now().replace(second=0).timestamp())
    start_time = int(end_time - datetime.timedelta(minutes=time_frame).total_seconds())
    timestamp_range = list(
        range(start_time + ONE_MINUTE_IN_SECONDS, end_time + ONE_MINUTE_IN_SECONDS, ONE_MINUTE_IN_SECONDS)
    )
    datetime_range = list(map(
        lambda timestamp: datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d %H:%M"),
        timestamp_range,
    ))

    # TCP SYN/ACk rate
    data = {
        "minutes": list(range(1, time_frame + 1)),
        "x_labels": datetime_range,
        "rate": [],
    }
    syn_ack_count_list = list(tcp_mongo_manager.find_tcp_ack_syn_count_per_minute(start_time, end_time))
    syn_count = {doc["timestamp"]: doc.get("syn_packets_count") for doc in syn_ack_count_list}
    ack_count = {doc["timestamp"]: doc.get("ack_packets_count") for doc in syn_ack_count_list}

    for timestamp in timestamp_range:
        syn_packets_count = syn_count.get(timestamp) or 0
        ack_packets_count = ack_count.get(timestamp) or 0
        try:
            data["rate"].append(syn_packets_count / ack_packets_count)
        except ZeroDivisionError:
            if syn_packets_count == 0:
                data["rate"].append(1)
            else:
                data["rate"].append(syn_packets_count)

    data["best_rate"] = [min((x for x in data["rate"] if x), key=lambda x:abs(x - 1)), ] * time_frame

    fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.2)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["rate"],
        "name": "SYN/ACK Rate",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines+markers",
    }, 1, 1)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["best_rate"],
        "name": "Best Rate",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines",
    }, 1, 1)

    # layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=data["minutes"],
            ticktext=data["x_labels"],
        ),
        font_size=10
    )
    fig["layout"]["margin"] = {
        "l": 0, "r": 0, "b": 0, "t": 0
    }
    fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

    return fig


@app.callback(Output("dns-packets-per-minute", "figure"),
              Input("interval-component", "n_intervals"))
def update_ip_graph_live(n):
    time_frame = 60

    end_time = int(datetime.datetime.now().replace(second=0).timestamp())
    start_time = int(end_time - datetime.timedelta(minutes=time_frame).total_seconds())
    timestamp_range = list(
        range(start_time + ONE_MINUTE_IN_SECONDS, end_time + ONE_MINUTE_IN_SECONDS, ONE_MINUTE_IN_SECONDS)
    )
    datetime_range = list(map(
        lambda timestamp: datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d %H:%M"),
        timestamp_range,
    ))

    data = {
        "minutes": list(range(1, time_frame + 1)),
        "x_labels": datetime_range,
    }

    dns_packets_count_list = list(dns_mongo_manager.find_packets_count_per_minute(start_time, end_time))

    total_dns_packets_count = {doc["timestamp"]: doc.get("packets_count", 0) for doc in dns_packets_count_list}
    small_dns_packets_count = {doc["timestamp"]: doc.get("small_packets_count", 0) for doc in dns_packets_count_list}
    huge_dns_packets_count = {doc["timestamp"]: doc.get("huge_packets_count", 0) for doc in dns_packets_count_list}

    data["total_packets"] = [total_dns_packets_count.get(timestamp, 0) for timestamp in timestamp_range]
    data["small_packets"] = [small_dns_packets_count.get(timestamp, 0) for timestamp in timestamp_range]
    data["huge_packets"] = [huge_dns_packets_count.get(timestamp, 0) for timestamp in timestamp_range]

    fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.2)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["total_packets"],
        "name": "Total DNS requests",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines+markers",
    }, 1, 1)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["small_packets"],
        "name": "Small DNS requests",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines+markers",
    }, 1, 1)

    fig.add_trace({
        "x": data["minutes"],
        "y": data["huge_packets"],
        "name": "Huge DNS requests",
        "text": data["x_labels"],
        "type": "scatter",
        "mode": "lines+markers",
    }, 1, 1)

    # layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=data["minutes"],
            ticktext=data["x_labels"],
        ),
        font_size=10
    )
    fig["layout"]["margin"] = {
        "l": 0, "r": 0, "b": 0, "t": 0
    }
    fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

    return fig


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
