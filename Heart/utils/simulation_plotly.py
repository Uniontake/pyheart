import argparse
import pandas as pd
import numpy as np
import os
import math
import plotly.graph_objects as go  # or plotly.express as px
import plotly.express as px
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import sys
import time

# AugumentParser
parser = argparse.ArgumentParser(description="Simulation Plotly By log_file")
parser.add_argument("log_file_dir", help="the log file or log file dir")
args = parser.parse_args()

log_file_dir = args.log_file_dir


def get_figure(logfile, dis_type="part"):
    dict_time, dict_value, dict_type = np.load(logfile)
    fig = go.Figure()
    #   add traces
    fig_id = 0
    columns_list = list(dict_time.keys())
    for col in columns_list:
        col_time = dict_time[col]
        col_value = dict_value[col]
        col_text = dict_type[col]
        # print(col_text)
        fig.add_trace(go.Scatter(x=col_time, y=col_value,
                                 yaxis="y" if fig_id == 0 else "y" + str(fig_id + 1), name=col))
        fig_id = fig_id + 1

    fig.update_traces(
        # hoverinfo="text+x+name",
        line={"width": 1},
        marker={"size": 4},
        mode="lines+markers",
    )

    #   update traces layout
    color_template = ['#673ab7', '#E91E63', '#795548', '#607d8b', '#2196F3',
                      '#EC7357', '#754F44', '#2E294E', '#56445D', '#353866', '#285943']

    trace_template = dict(
        anchor="x",
        autorange=True,
        domain=[0, 0.14],
        linecolor="#673ab7",
        mirror=True,
        range=[0, 1],
        showline=True,
        tickfont={"color": "#673ab7"},
        tickmode="auto",
        ticks="",
        titlefont={"color": "#673ab7"},
        type="linear",
        zeroline=False
    )

    the_layout = {
        'xaxis': dict(
            autorange=True,
            range=[str(min(min(dict_time))), str(max(max(dict_time)))]
        )
    }

    trace_num = len(columns_list)

    for i in range(trace_num if dis_type == 'part' else 1):
        col_trace = trace_template.copy()
        col_trace['domain'] = [(i) * (1 / trace_num), (i + 1) * (1 / trace_num)] if dis_type == 'part' else [0, 1]
        col_trace['linecolor'] = color_template[i % 11]
        col_trace['range'] = [min(dict_value[col]), max(dict_value[col])] if dis_type == 'part' else [
            min(min(dict_value)), max(max(dict_value))]
        col_trace['tickfont'] = {"color": color_template[i % 11]}
        col_trace['titlefont'] = {"color": color_template[i % 11]}
        the_layout['yaxis' if i == 0 else 'yaxis' + str(i + 1)] = col_trace

    fig.update_layout(
        # title = the_model_filename,
        dragmode="zoom",
        hovermode="x",
        legend=dict(traceorder="reversed"),
        height=1000,
        template="plotly_white",
        margin=dict(
            t=100,
            b=100
        )
    )

    fig.update_layout(**the_layout)

    return fig


dict_time_list = [{} for i in range(len(model_filename))]
dict_value_list = [{} for i in range(len(model_filename))]
dict_type_list = [{} for i in range(len(model_filename))]


def Run_Model_Query(model_id):
    dict_time_list[model_id], dict_value_list[model_id], dict_type_list[model_id] = Simulation(model_filename[model_id])


for i in range(model_number):
    Run_Model_Query(i)

# Dash Plotly

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Record the buttom n_clicks
last_nclicks = None

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([

        html.Div([
            html.Label('Model Selcetion'),
            html.Br(),
            dcc.Dropdown(
                id='model-filename',
                options=[{'label': model_filename[i], 'value': i} for i in range(len(model_filename))],
                value=0
            ),
        ]),
    ]),
    html.Br(),
    dcc.Graph(id='uppaal-graphic')
])


@app.callback(
    Output(component_id='uppaal-graphic', component_property='figure'),
    Input(component_id='model-filename', component_property='value'),
)
def select_figure(model_id):
    model_id = int(model_id)
    # print(list(dict_time_list[model_id].keys()))
    fig = Uppaal_Plotly(dict_time_list[model_id], dict_value_list[model_id], dict_type_list[model_id])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
