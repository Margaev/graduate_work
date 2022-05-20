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
IP_PACKETS_COLLECTION = os.environ.get("DATABASE", "ip_packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    [
        HEADING,
        IP_PACKETS_PER_MINUTE,
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]
)


@app.callback(Output("ip-packets-per-minute", "figure"),
              Input("interval-component", "n_intervals"))
def update_graph_live(n):
    mongo_manager = MongoManager(
        host=MONGO_HOST,
        port=MONGO_PORT,
        database=DATABASE,
        collection=IP_PACKETS_COLLECTION,
        username=USERNAME,
        password=PASSWORD,
    )

    time_frame = 60

    end_time = int(datetime.datetime.now().replace(second=0).timestamp())
    start_time = int(end_time - datetime.timedelta(minutes=time_frame).total_seconds())
    timestamp_range = list(
        range(start_time + ONE_MINUTE_IN_SECONDS, end_time + ONE_MINUTE_IN_SECONDS, ONE_MINUTE_IN_SECONDS)
    )
    datetime_range = map(
        lambda timestamp: datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d %H:%M"),
        timestamp_range,
    )

    data = {
        "minutes": list(range(1, time_frame + 1)),
        "x_labels": list(datetime_range),
    }

    ip_packets_count_list = mongo_manager.find_ip_packets_count_per_minute(start_time, end_time)
    ip_packets_count = {doc["timestamp"]: doc["packets_count"] for doc in ip_packets_count_list}
    data["packets"] = [ip_packets_count.get(timestamp, 0) for timestamp in timestamp_range]

    data["median"] = (mongo_manager.get_median_ip_packets_count_per_minute(start_time, end_time), ) * time_frame

    # subplots
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
        "mode": "lines+markers",
    }, 1, 1)

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=data["minutes"],
            ticktext=data["x_labels"],
        )
    )
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    return fig


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
