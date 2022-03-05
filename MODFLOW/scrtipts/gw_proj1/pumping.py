import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import flopy


class Pumping(object):
    def __init__(self):
        """

        """
        self.municipal_pumping_raw_file = ''
        self.aggricultral_pumping_file = ''
        self.rural_pumping_file = ''


    def process_municipal_pumping(self):
        # read raw data for pumping
        self.extract_municip_data()
        pass

    def extract_municip_data(self):
        """
        :return: (1) a dictionary for pumping includes {well_id: name, x, y,z, perftop, perf_bot, pumping_timeseries,
        digging_date}
                 (2) csv file [well_id, name, x, y, perf, time, pumping]

        """
        sheet = self.municipal_pumping_raw_file['pumping_data_sheet']
        df = pd.read_excel(self.municipal_pumping_raw_file['file_name'], sheet_name=sheet)


        pass





if __name__ == "__main__":

    rr_pumping = Pumping()
    rr_pumping.municipal_pumping_raw_file = {
        'file_name': r"D:\Workspace\projects\RussianRiver\Data\Pumping\Municipal_Pumping" \
                                            r"\Pumping_RR_SBworking(02-06-2018).xlsx",
        'pumping_data_sheet': r"monthly data (AF)",
        'Well_info_sheet'   : r"location and perf and log"
         }

    rr_pumping.process_municipal_pumping()


    pass

