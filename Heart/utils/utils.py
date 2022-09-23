import numpy as np
import os
import json
import plotly.graph_objects as go # or plotly.express as px


# set random seed
def set_seed(seed=None):
    if seed is not None:
        np.random.seed(seed)


def load_json(jsonfile):
    with open(jsonfile, 'r') as f:
        # 文件数据获取
        data = json.load(f)
        data["filename"] = os.path.splitext(os.path.basename(jsonfile))[0]
    return data


def cal_gauss(time_mean, time_sd):
    number = time_sd * np.random.randn() + time_mean
    return int(np.round(number))


def cal_uniform(time_min, time_max):
    number = np.random.uniform(time_min, time_max)
    return int(np.floor(number))


def cal_exponential(ex_lambda):
    number = np.random.exponential(ex_lambda)
    return int(np.floor(number))


def random_pick(some_list, probabilities):
    x = np.random.uniform(0, 1)
    cumulative_probability = 0.0
    pro_sum = sum(probabilities)
    probabilities = [(i / pro_sum) for i in probabilities]
    # print(probabilities)
    item_state = None
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            item_state = item
            break
    return item_state


def plotly_one_figure(sam_dict, dis_type="part"):
    dict_time, dict_value, dict_type, output_log = sam_dict
    fig = go.Figure()
    #   add traces
    fig_id = 0
    columns_list = list(dict_time.keys())
    # col_text = 0
    for col in columns_list:
        col_time = dict_time[col]
        col_value = dict_value[col]
        col_text = dict_type[col]
        # print(len(col_text))
        # print(len(col_time))
        fig.add_trace(go.Scatter(x=col_time, y=col_value,hovertext=col_text,
                                 yaxis="y" if fig_id == 0 else "y" + str(fig_id + 1), name=col))
        fig_id = fig_id + 1

    fig.update_traces(
        hoverinfo="text+x+name",
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
        title = "A and V Trace",
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


if __name__ == "__main__":
    pass
