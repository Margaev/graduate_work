import os
import datetime

import dash
import numpy as np
import plotly
import plotly.subplots
import plotly.express
from dash.dependencies import Input, Output
from dash import dcc, html

from data_models.models import PacketModel
from helpers.mongo import MongoManager

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
DATABASE = os.environ.get("DATABASE", "network_scanner")
COLLECTION = os.environ.get("DATABASE", "packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

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
            interval=5 * 1000,  # in milliseconds
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
        collection=COLLECTION,
        username=USERNAME,
        password=PASSWORD,
    )

    time_frame = 60

    data = {
        "minutes": np.arange(time_frame, dtype=int),
        "x_labels": np.empty(time_frame, dtype="U11"),
        "packets": np.zeros(time_frame, dtype=int),
        "mean": np.array([None, ] * time_frame, dtype=float),
    }

    start_time = datetime.datetime.now() - datetime.timedelta(minutes=time_frame - 1)

    for i in range(time_frame):
        desired_datetime = start_time + datetime.timedelta(minutes=i)
        num_of_packets = mongo_manager.find_num_of_ip_packets_per_minute(
            dtm=desired_datetime
        )
        data["x_labels"][i] = desired_datetime.strftime("%m/%d %H:%M")
        data["packets"][i] = num_of_packets

    # Mean IP packets per minute
    starting_index = (data["packets"] != 0).argmax(axis=0)

    data["mean"][starting_index:] = np.mean(
        data["packets"][
            # drop 0 values
            (data["packets"] != np.array(0))
            # truncating everything below 20th and above 80th percentile
            & (data["packets"] > np.percentile(data["packets"], 5))
            & (data["packets"] < np.percentile(data["packets"], 95))
        ]
    )

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
        "y": data["mean"],
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
