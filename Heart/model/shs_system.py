# from ..utils.utils import *
import os
import datetime
import numpy as np

from .heart_class import *


class SHSNetwork(object):
    """
    Heart-ICD environment
    """

    def __init__(self, parameters_dicts):
        self.__Only_id = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d_%H_%M_%S')
        self.__Parameters_dicts = parameters_dicts
        self.__patient_filename = parameters_dicts["filename"]
        self.__HA = HeartNode(self.__Parameters_dicts["HA"])
        self.__Path_A2AV = HeartPath(self.__Parameters_dicts["Path_A2AV"])
        self.__HAV = HeartNode(self.__Parameters_dicts["HAV"])
        self.__Path_AV2V = HeartPath(self.__Parameters_dicts["Path_AV2V"])
        self.__HV = HeartNode(self.__Parameters_dicts["HV"])

        self.__Cur_clock = 0
        self.__Cur_configuration = [self.__HA.current_state(), self.__Path_A2AV.current_state(),
                                    self.__HAV.current_state(),
                                    self.__Path_AV2V.current_state(), self.__HV.current_state()]

        self.__A_retro, self.__A_in = False, False
        self.__AV_A, self.__A_AV, self.__AV_V, self.__V_AV = False, False, False, False
        self.__A_AV2, self.__V_AV2 = False, False
        self.__V_NSR, self.__V_in = False, False
        self.__V_NSR2, self.__A_retro2 = False, False
        self.__simulation_count = 0

    def __reset_channel(self):
        self.__A_retro, self.__A_in = False, False
        self.__AV_A, self.__A_AV, self.__AV_V, self.__V_AV = False, False, False, False
        self.__A_AV2, self.__V_AV2 = False, False
        self.__V_NSR, self.__V_in = False, False
        self.__V_NSR2, self.__A_retro2 = False, False


    def __current_configuration(self):
        self.__Cur_configuration = [self.__HA.current_state(), self.__Path_A2AV.current_state(),
                                    self.__HAV.current_state(),
                                    self.__Path_AV2V.current_state(), self.__HV.current_state()]
        return self.__Cur_configuration

    def __equiv_configuration(self, last_configuration):
        for i in range(len(self.__Cur_configuration)):
            if last_configuration[i] != self.__Cur_configuration[i]:
                return False
        return True

    def __clock_increase(self):
        self.__Cur_clock = self.__Cur_clock + 1
        self.__HA.clock_increase()
        self.__Path_A2AV.clock_increase()
        self.__HAV.clock_increase()
        self.__Path_AV2V.clock_increase()
        self.__HV.clock_increase()


    @property
    def __step(self):
        vis_channel = {"AS": {"value": 0, "type": "A_NSR"}, "VS": {"value": 0, "type": "V_NSR"}}

        while True:
            last_configuration = self.__current_configuration()

            self.__A_in = self.__HA.step(self.__A_retro)
            if self.__A_in:
                vis_channel["AS"]["value"] = 1
                vis_channel["AS"]["type"] = ("A_retro" if self.__A_retro else "A_NSR")
                # print(vis_channel["AS"]["type"])
            self.__A_retro = False

            self.__A_AV2, self.__A_retro = self.__Path_A2AV.step(self.__A_in, self.__AV_A)
            self.__A_in = self.__AV_A = False
            self.__A_AV = self.__A_AV or self.__A_AV2

            self.__AV_A = self.__AV_V = self.__HAV.step(self.__A_AV or self.__V_AV)
            self.__A_AV = self.__V_AV = self.__A_AV2 = False

            self.__V_NSR2, self.__V_AV = self.__Path_AV2V.step(self.__AV_V, self.__V_in)
            self.__AV_V = self.__V_in = False
            self.__V_NSR = self.__V_NSR or self.__V_NSR2

            self.__V_in = self.__HV.step(self.__V_NSR)
            if self.__V_in:
                vis_channel["VS"]["value"] = 1
                vis_channel["VS"]["type"] = ("V_NSR" if self.__V_NSR else "V_tachy")
                # print(vis_channel["VS"]["type"])
            self.__V_NSR = self.__V_NSR2 = False

            self.__V_NSR, self.__V_AV2 = self.__Path_AV2V.step(self.__AV_V, self.__V_in)
            self.__AV_V = self.__V_in = False
            self.__V_AV = self.__V_AV or self.__V_AV2

            # PATH没返回True
            # print(self.__A_AV, self.__V_AV)
            self.__AV_A = self.__AV_V = self.__HAV.step(self.__A_AV or self.__V_AV)
            # print(self.__AV_A, self.__AV_V)
            self.__A_AV = self.__V_AV = self.__V_AV2 = False

            self.__A_AV, self.__A_retro2 = self.__Path_A2AV.step(self.__A_in, self.__AV_A)
            self.__A_in = self.__AV_A = False
            self.__A_retro = self.__A_retro or self.__A_retro2

            self.__A_in = self.__HA.step(self.__A_retro)
            if self.__A_in:
                vis_channel["AS"]["value"] = 1
                vis_channel["AS"]["type"] = ("A_retro" if self.__A_retro else "A_NSR")
                # print(vis_channel["AS"]["type"])
            self.__A_retro = self.__A_retro2 = False

            if self.__equiv_configuration(last_configuration):
                break
        # print(self.__current_configuration())
        self.__reset_channel()
        return vis_channel

    def reset(self):
        """
        reset environment
        @return: None
        """
        self.__reset_channel()
        self.__Cur_clock = 0
        self.__HA.reset()
        self.__HV.reset()
        self.__Path_A2AV.reset()
        self.__Path_AV2V.reset()
        self.__simulation_count = 0
        self.__Cur_configuration = [self.__HA.current_state(), self.__Path_A2AV.current_state(),
                                    self.__HAV.current_state(),
                                    self.__Path_AV2V.current_state(), self.__HV.current_state()]

    def update_patient_digital_twin(self, parameters_dicts):
        only_id = self.__Only_id
        now_clock = self.__Cur_clock
        s_count = self.__simulation_count
        self.__init__(parameters_dicts)
        # reload simulation
        self.__Only_id = only_id
        self.__Cur_clock = now_clock
        self.__simulation_count = s_count

    def simulation(self, sim_time, save_plotly=False, save_dir=''):
        """
        simulation the digital twin
        @param sim_time: the simulation time bound: int
        @param save_plotly: whether save the plotly log: bool
        @param save_dir: is save_plotly is true, save log to save_dir
        @return: the simulation output: dict
        """
        self.__simulation_count = self.__simulation_count + 1
        # PPV = TP / (TP + FP)
        simulation_output = {"Only_id": self.__Only_id, "AS_array": [], "VS_array": []}
        columns_list_name, sam_dict_time, sam_dict_value, sam_dict_type = [], {}, {}, {}
        start_time = self.__Cur_clock
        last_vis_channel = {}
        vis_channel = {}
        for i in range(start_time, start_time + sim_time):
            vis_channel = self.__step
            if i == start_time:
                last_vis_channel = vis_channel.copy()
            # only return simulation_output
            if vis_channel["AS"]["value"] == 1:
                simulation_output["AS_array"].append(i)
            if vis_channel["VS"]["value"] == 1:
                simulation_output["VS_array"].append(i)

            if save_plotly:
                if i == start_time:
                    columns_list_name = vis_channel.keys()
                    for col_name in columns_list_name:
                        sam_dict_time[col_name] = [start_time]
                        sam_dict_value[col_name] = [vis_channel[col_name]["value"]]
                        sam_dict_type[col_name] = [vis_channel[col_name]["type"]]
                else:
                    for col_name in columns_list_name:
                        if last_vis_channel[col_name]["value"] != vis_channel[col_name]["value"]:
                            sam_dict_time[col_name].append(i - 1)
                            sam_dict_value[col_name].append(last_vis_channel[col_name]["value"])
                            sam_dict_type[col_name].append(last_vis_channel[col_name]["type"])
                            sam_dict_time[col_name].append(i)
                            sam_dict_value[col_name].append(vis_channel[col_name]["value"])
                            sam_dict_type[col_name].append(vis_channel[col_name]["type"])

            last_vis_channel = vis_channel.copy()
            self.__clock_increase()

        if save_plotly:
            for col_name in columns_list_name:
                sam_dict_time[col_name].append(start_time + sim_time - 1)
                sam_dict_value[col_name].append(vis_channel[col_name]["value"])
                sam_dict_type[col_name].append(vis_channel[col_name]["type"])
            # save plotly log
            sam_save_dict_list = np.array([sam_dict_time, sam_dict_value, sam_dict_type, simulation_output])
            if len(save_dir) != 0 and save_dir[-1] != '/':
                save_dir = save_dir + '/'
            log_save_dir = save_dir + self.__Only_id + '/'
            if not os.path.exists(log_save_dir):
                os.makedirs(log_save_dir)
            log_save_filename = log_save_dir + str(self.__simulation_count) + "_" + self.__patient_filename + '_' + str(
                start_time) + '_' + str(
                self.__Cur_clock) + '.npy'
            np.save(log_save_filename, sam_save_dict_list)

        return simulation_output
