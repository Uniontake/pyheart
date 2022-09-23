from ..utils.utils import *


class HeartNode(object):
    """Heart Node Class, including HA, HV, HAV."""

    def __init__(self, parameters_dicts):
        # State (initial)
        self.Rest_Min = None
        self.Condition = None
        self.Rest_Max = None
        self.ERP_Min = None
        self.ERP_Max = None
        self.RRP_Max = None
        self.RRP_Min = None
        self.Cur_state = "Rest"
        self.Mode = "0"
        self.Next_Mode = "0"
        # Parameters
        self.Parameters_dicts = parameters_dicts
        self.__setup()
        # clock
        self.Cur_clock = 0

        # Entry variables
        self.Rest_time = cal_uniform(self.Rest_Min, self.Rest_Max)
        self.ERP_time = cal_uniform(self.ERP_Min, self.ERP_Max)
        self.RRP_time = cal_uniform(self.RRP_Min, self.RRP_Max)

    def __setup(self):
        self.Mode = self.Next_Mode
        self.Condition = self.Parameters_dicts[self.Mode]["name"]
        self.Rest_Min = self.Parameters_dicts[self.Mode]["value"][0]
        self.Rest_Max = self.Parameters_dicts[self.Mode]["value"][1]
        self.ERP_Min = self.Parameters_dicts[self.Mode]["value"][2]
        self.ERP_Max = self.Parameters_dicts[self.Mode]["value"][3]
        self.RRP_Min = self.Parameters_dicts[self.Mode]["value"][4]
        self.RRP_Max = self.Parameters_dicts[self.Mode]["value"][5]

    def __entry(self, next_state):
        self.__setup()
        if next_state == "Rest":
            self.Rest_time = cal_uniform(self.Rest_Min, self.Rest_Max)
        elif next_state == "ERP":
            self.ERP_time = cal_uniform(self.ERP_Min, self.ERP_Max)
        else:
            self.RRP_time = cal_uniform(self.RRP_Min, self.RRP_Max)
        self.Cur_clock = 0
        self.Cur_state = next_state

    def current_condition(self):
        return self.Condition

    def current_state(self):
        return self.Cur_state

    def current_clock(self):
        return self.Cur_clock


    def clock_increase(self):
        self.Cur_clock = self.Cur_clock + 1

    def step(self, act_node):
        conduct: bool = False
        if self.Cur_state == "Rest":
            if act_node:
                self.__entry("ERP")
                self.step(False)
                conduct = True
            if self.Cur_clock >= self.Rest_time:
                self.__entry("ERP")
                self.step(False)
                conduct = True
        elif self.Cur_state == "ERP":
            if self.Cur_clock >= self.ERP_time:
                self.__entry("RRP")
                self.step(False)
        else:
            if act_node:
                self.__entry("ERP")
                self.step(False)
                conduct = True
            if self.Cur_clock >= self.RRP_time:
                self.__entry("Rest")
                self.step(False)
        return conduct

    def reset(self):
        # State (initial)
        self.Cur_state = "Rest"
        self.Mode = "0"
        self.Next_Mode = "0"
        # Parameters
        # self.Parameters_dicts = Parameters_dicts
        self.__setup()
        # clock
        self.Cur_clock = 0

        # Entry variables
        self.Rest_time = cal_uniform(self.Rest_Min, self.Rest_Max)
        self.ERP_time = cal_uniform(self.ERP_Min, self.ERP_Max)
        self.RRP_time = cal_uniform(self.RRP_Min, self.RRP_Max)


class HeartPath(object):
    """The conduction path from HA to HAV, or from HAV to HV"""

    def __init__(self, parameters_dicts):
        # State (initial)
        self.Cur_state = "Idle"
        # Parameters
        self.Parameters_dicts = parameters_dicts
        self.Condition = self.Parameters_dicts["0"]["name"]
        self.CondTime_min = self.Parameters_dicts["0"]["value"][0]
        self.CondTime_max = self.Parameters_dicts["0"]["value"][1]
        # clock
        self.Cur_clock = 0

        # Entry variables
        self.Cond_time = 0

    def __entry(self, next_state):
        if next_state != "Idle":
            self.Cond_time = cal_uniform(self.CondTime_min, self.CondTime_max)
        self.Cur_clock = 0
        self.Cur_state = next_state

    def current_condition(self):
        return self.Condition

    def current_state(self):
        return self.Cur_state

    def current_clock(self):
        return self.Cur_clock

    def clock_increase(self):
        self.Cur_clock = self.Cur_clock + 1

    def step(self, act_path_ord, act_path_rev):
        conduct_ord: bool = False
        conduct_rev: bool = False
        if self.Cur_state == "Idle":
            if act_path_ord:
                self.__entry("Order")
                self.step(False, False)
            if act_path_rev:
                self.__entry("Reverse")
                self.step(False, False)
        elif self.Cur_state == "Order":
            if act_path_rev:
                self.__entry("Idle")
                self.step(False, False)
            if self.Cur_clock >= self.Cond_time:
                self.__entry("Idle")
                self.step(False, False)
                conduct_ord = True
        else:
            if act_path_ord:
                self.__entry("Idle")
                self.step(False, False)
            if self.Cur_clock >= self.Cond_time:
                self.__entry("Idle")
                self.step(False, False)
                conduct_rev = True
                # print("True")

        return conduct_ord, conduct_rev

    def reset(self):
        self.Cur_state = "Idle"
        # Parameters
        # self.Parameters_dicts = Parameters_dicts
        self.Condition = self.Parameters_dicts["0"]["name"]
        self.CondTime_min = self.Parameters_dicts["0"]["value"][0]
        self.CondTime_max = self.Parameters_dicts["0"]["value"][1]
        # clock
        self.Cur_clock = 0

        # Entry variables
        self.Cond_time = 0




if __name__ == "__main__":
    """
    Testing
    """
    jsonFilename = '../../Patients/Patient1/Patient1_Parameters.json'
    data = load_json(jsonFilename)
    Parameters_dicts = data["HA"]
    HA = HeartNode(Parameters_dicts)
