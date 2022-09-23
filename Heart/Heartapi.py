"""
Use:
HeartICD.XXX()
"""
from .utils.utils import *
from .model import shs_system
# import plotly.express as px
import numpy as np
import os
import math


def get_system_instance(json_filename):
    """
    获取环境实例
    @param json_filename: model parameters table: dict
    @return: SHSNetwork object: SHSNetwork
    """
    data = load_json(json_filename)
    Sys = shs_system.SHSNetwork(data)
    return Sys


def update_system_instance(Sys: shs_system.SHSNetwork, json_filename: str):
    """
    @param sys: original environment: SHSNetwork
    @param json_filename: new model parameters table: dict
    @return: SHSNetwork
    """
    data = load_json(json_filename)
    Sys.update_patient_digital_twin(data)


def plotly_system_log(log_file_dir: str, run_jupyter=True):
    """
    plot the system log
    @param log_file_dir: log file or log file dir: string
    @param run_jupyter: run jupyter or dash: bool
    @return:
    """
    log_files = []
    if os.path.isdir(log_file_dir):
        log_files = os.listdir(log_file_dir)
        log_files = [os.path.join(log_file_dir, x) for x in log_files]
    else:
        log_files = [log_file_dir]

    sam_dict_list = [np.load(files, allow_pickle=True) for files in log_files]
    figs = [plotly_one_figure(sam_dict) for sam_dict in sam_dict_list]
    # Now only plotly one
    # print(sam_dict_list[0][3])
    figs[-1].show()
