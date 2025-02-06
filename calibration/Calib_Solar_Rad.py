import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar
from pest import calibration


def compute_SR_mon_ave(stat, solr_rad_stat):
    all_sr_av = dict()
    for key in solr_rad_stat:
        id = stat.stat_dict[key][0]['ID']
        curr_rad = stat.stat_dict[key][1]
        date = stat.stat_dict['Date']
        sr_av = dict()
        i = 0
        for dd in date:
            try:
                sr_av[dd.month] = 0.5* curr_rad[i] + 0.5 * sr_av[dd.month]
            except:
                sr_av[dd.month] = curr_rad[i]

            i = i + 1

        sr = []
        for m in range(1,13):
            sr.append([m,sr_av[m]])

        all_sr_av[id] = np.array(sr)
    return all_sr_av




def plot_sim_vs_meas(stat,df, solr_rad_stat, hrus):
    for st in solr_rad_stat:
        plt.figure()
        hru_id = stat.stat_dict[st][0]['ID']
        curr_data = df.loc[:, hrus == hru_id]
        curr_station_nm = curr_data.columns[0]
        curr_ms_solrad = curr_data.values[1:]
        plt.scatter(sim_sr_av[hru_id][:,0],curr_ms_solrad,color = 'red')
        plt.plot(sim_sr_av[hru_id][:,0], sim_sr_av[58328][:,1])
        plt.title(curr_station_nm)
        plt.xlabel("Month")
        plt.ylabel("Solar Radiation [Langleys]")



if __name__ == "__main__":
    if False:
        cname = "D:\Workspace\projects\RussianRiver\gsflow\prms2\windows\prms_rr.control"
        prms = prms_py.Prms_base()
        prms.control_file_name = cname
        prms.load_prms_project()
        prms.run()
        # bud = Budget(prms)
        stat = Statistics(prms)
        inputs = dict()
        inputs['model'] = prms
        inputs['output']= stat

        # Read observation
        sol_rad_excel = r"D:\Workspace\projects\RussianRiver\calibration\solar_radiation_data\mean_monthly_solar_rad.xlsx"
        df = pd.read_excel(sol_rad_excel, sheetname='mean monthly')
        inputs['df'] = df
        solr_rad_stat = ['swrad_1', 'swrad_2']
        inputs['solr_rad_stat'] = solr_rad_stat
        sim_sr_av = compute_SR_mon_ave(stat, solr_rad_stat)
        hrus = df.loc[0].values
        plot_sim_vs_meas(stat,df, solr_rad_stat , hrus)
        plt.show()

    all_params = {'dday_slope':[0.2, 0.7], 'dday_intcp':[-60, 4], 'radj_sppt' : [0.0, 1.0],
                  'radj_wppt':[0.0, 1.0], 'radadj_slope':[0.0, 1.0],
                  'radadj_intcp':[0.0,1.0], 'radmax':[0.0, 1.0], 'ppt_rad_adj':[0.0, 0.5],
                  'tmax_index':[-10, 110], 'tmax_allrain':[0.0,90.0]}
    par_to_calib = {'dday_slope':[0.2, 0.7], 'dday_intcp':[-60, 4], 'tmax_index':[-10, 110]}

    ### ************** Calibration Setting **************************
    ### step (1): Prepare names for parameters to calibrate
    para = []
    for i in range(1,13):
        para.append(("dday_inctp_" + str(i)))
    for i in range(1,13):
        para.append(("dday_slope_" + str(i)))

    cal_proj = calibration.Calibration()
    cal_proj.control.MParam.filename = 'solar_rad.tpl'
    cal_proj.control.MParam.param_data = para
    cal_proj.control.MParam.write_file()

    ### step (2): prepare observations
    obs = []
    for i in np.arange(len(yo)):
        obs.append("obs1%d" % (i))

    cal_proj.control.MObser.obs_data = obs
    cal_proj.control.MObser.filename = 'test.ins'
    cal_proj.control.MObser.obs_data['obs_val'] = yo
    cal_proj.control.MObser.write_ins_file()
    cal_proj.control.filename = "test.pst"
    cal_proj.control.INFLE = 'input.dat'
    cal_proj.control.OUTFLE = 'output.dat'
    cal_proj.generate_model_batch_file('runmodel.bat')
    cal_proj.control.write()

    pass


















# plot







