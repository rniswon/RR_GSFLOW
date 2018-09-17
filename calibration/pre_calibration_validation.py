import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar
from pyprms import prms_only_plots


## check temprature distributions
hru_table = pd.read_pickle('D:\Workspace\projects\RussianRiver\gsflow\hru_att_tableTemp.pkl')
tmin = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Climate_data\Filled_tmin.csv")
tmax = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Climate_data\Filled_tmax.csv")
temp_stat_info = [['HEALDSBURG','USC00043875',1, 73774], # [name, id, zone_id, hru_id] 73774
                  ['UKIAH', 'USC00049122', 2, 24089], # 24089
                  ['Sanel Valley','106',3, 39556],
                  ['Santa Rosa', '83', 4, 94037],
                  ['HAWKEYE CALIFORNIA', 'USR0000CHAW', 5, 58328],
                  ['POTTER VALLEY P H','USC00047109',6, 3872],
                  ['LYONS VALLEY CALIFOR','USR0000CLYO',7, 26152],
                  ['SANTA ROSA CALIFORNI', 'USR0000CSRS', 8, 86724 ]]

cname = "D:\Workspace\projects\RussianRiver\gsflow\prms2\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()
hru_table = pd.read_pickle('D:\Workspace\projects\RussianRiver\gsflow\hru_att_table.pkl')
prmsplot = prms_only_plots.Plotter(hru_shp = hru_table, proj = prms)
#prmsplot.plot2D('hru_tsta')
prmsplot.plot2D('hru_tlaps')
prms.run()
stat = Statistics(prms)

for key in stat.stat_dict.keys():
    var_type = key.split('_')[0]
    var_type = var_type.replace('c', '')

    if ( var_type in ['tmin', 'tmax']):
        curr_id = stat.stat_dict[key][0]['ID']
        sim_var = stat.stat_dict[key][1]
        for st in temp_stat_info:
            curr_st_name =[]
            if st[3]== curr_id:
                curr_st_name = st[1]
                break
        if var_type == 'tmin':
            meas_var = tmin[curr_st_name]
        elif var_type == 'tmax':
            meas_var = tmax[curr_st_name]

        meas =  meas_var.values[0:len(sim_var)]
        plt.plot(sim_var)
        plt.plot(meas, 'r')
        msg = var_type + ' at ' + curr_st_name
        plt.title(msg)
        pass






x = 1
pass


## validate ppt
ppt_zones = np.load('D:\Workspace\projects\RussianRiver\Climate_data\ppt_zone_dict.npy')
ppt_zones = ppt_zones.all()
