from pest import calibration
import pandas as pd
import numpy as np
import datetime
import copy
from gispy import shp
import matplotlib.pyplot as plt


def read_obs_file(fn):
    fid = open(fn, 'r')
    content = fid.readlines()
    fid.close()
    obs_values = []
    obs_names = []
    obs_loc_type = []
    obs_loc_id = []
    obs_info = dict()
    # parse file
    for line in content:
        try:
            marker = line.strip().split()[0]
        except:
            pass
        if marker == '#':  # comment
            pass
        elif marker == '$':  # measurement name
            meas_base_name = line.strip().split()[1]
            # remove any comments
            line = line.split("#")
            line = line[0]
            num_of_obs = int(line.strip().split('%')[1])

            for n in range(num_of_obs):
                obs_names.append((meas_base_name + "_" + str(n)))

        elif marker == "*":
            element_type = line.strip().split()[1]
            # remove any comments
            line = line.split("#")
            line = line[0]
            element_id = int(line.strip().split('%')[1])

        else:  # read values
            obs_values.append(float(line.strip()))
            obs_loc_type.append(element_type)
            obs_loc_id.append(element_id)
    obs_info['obs_values'] = obs_values
    obs_info['obs_names'] = obs_names
    obs_info['obs_loc_type'] = obs_loc_type
    obs_info['obs_loc_id'] = obs_loc_id
    return obs_info


def read_nwis_gages(fn):
    gage_flow = dict()
    prevname = ""
    with open(fn, 'r') as fid:
        for line in fid:
            if line.startswith('USGS'):
                parts = line.split()
                name = parts[1]
                if name != prevname:
                    print name
                date = datetime.datetime.strptime(parts[2], '%Y-%m-%d')
                try:
                    flow = float(parts[3])
                    if parts[4] == 'A':
                        approve = 1
                except:
                    flow = np.nan
                    approve = 0

                cur_record = [date, flow, approve]
                if name in gage_flow.keys():
                    gage_flow[name].append(cur_record)
                else:
                    gage_flow[name] = [cur_record]
                prevname = copy.deepcopy(name)

    for key in gage_flow:
        gage_flow[key] = np.array(gage_flow[key])
    np.save("nwis_gage_data.npy", gage_flow)


def compute_stream_volume_average(df, gage_flow, start_date, end_date, att_table):
    obs_data = {}
    for gage in att_table['NAME'].values:
        # the shape file has attribute for the gage id in the model and the gage name
        ann_mean = []
        monthly_mean = []
        if gage in gage_flow.keys():
            loc = [att_table['NAME'].values == gage]
            gage_id = att_table['ZONE_VALUE'].values[loc]
            gage_data = gage_flow[gage]
            loc_start_date = gage_data[:, 0] >= start_date
            loc_end_date = gage_data[:, 0] <= end_date
            time_mask = np.logical_and(loc_start_date, loc_end_date)
            curr_data = gage_data[time_mask, :]
            if len(curr_data) > 0:
                year_month = [[curr_dat.year, curr_dat.month] for curr_dat in curr_data[:, 0]]
                year_month = np.array(year_month)
                years_in_record = np.unique(year_month[:, 0])
                for year in years_in_record:
                    loc = year_month[:, 0] == year
                    months_in_this_year = year_month[loc, 1]
                    if year >= start_date.year and year <= end_date.year:
                        fll = np.nanmean(curr_data[loc, 1].astype('float'))
                        if np.logical_not(np.isnan(fll)):
                            ann_mean.append([year, fll])

                    for mon in range(1, 13):
                        if mon in months_in_this_year:
                            locm = year_month[:, 1] == mon
                            locm2 = np.logical_and(locm, loc)
                            if year >= start_date.year and year <= end_date.year:
                                ffl2 = np.nanmean(curr_data[locm2, 1].astype("float"))
                                if np.logical_not(np.isnan(ffl2)):
                                    monthly_mean.append([year, mon, ffl2])

                if len(monthly_mean) > 0 or len(ann_mean) > 0:
                    obs_data[gage_id[0]] = {"gage_name": gage, "monthly_mean": np.array(monthly_mean),
                                            "annual_mean": np.array(
                                                ann_mean)}
            else:
                pass  # no data for current gage

    return obs_data


def compute_imp_stream_volume_average(df, gage_flow, start_date, end_date, att_table):
    obs_data = {}
    gages_names = df.columns[1:]

    for gage in gages_names:
        ann_mean = []
        monthly_mean = []
        loc = [att_table['NAME'].values == str(gage)]
        gage_id = att_table['ZONE_VALUE'].values[loc]
        gage_data = df[gage].values
        df_dates = pd.DatetimeIndex(df['Date'])

        loc_start_date = df['Date'].values >= np.array(start_date, 'datetime64')
        loc_end_date = df['Date'].values <= np.array(end_date, 'datetime64')
        time_mask = np.logical_and(loc_start_date, loc_end_date)

        curr_data = gage_data[time_mask]
        if len(curr_data) > 0:
            cur_dates = df_dates[time_mask]
            year_month = [[curr_dat.year, curr_dat.month] for curr_dat in cur_dates]
            year_month = np.array(year_month)
            years_in_record = np.unique(year_month[:, 0])

            for year in years_in_record:
                loc = year_month[:, 0] == year
                months_in_this_year = year_month[loc, 1]
                if year >= start_date.year and year <= end_date.year:
                    flow2 = np.nanmean(curr_data[loc].astype('float')) * (35.3147 / 24 / 60 / 60)
                    if np.logical_not(np.isnan(flow2)):
                        ann_mean.append([year, flow2])

                for mon in range(1, 13):
                    if mon in months_in_this_year:
                        locm = year_month[:, 1] == mon
                        locm2 = np.logical_and(locm, loc)
                        if year >= start_date.year and year <= end_date.year:
                            flow = np.nanmean(curr_data[locm2].astype("float")) * (35.3147 / 24 / 60 / 60)
                            if np.logical_not(np.isnan(flow2)):
                                monthly_mean.append([year, mon, flow])

                if len(gage_id) > 0:
                    if len(monthly_mean) > 0 or len(ann_mean) > 0:
                        obs_data[gage_id[0]] = {"gage_name": gage, "monthly_mean": np.array(monthly_mean),
                                                "annual_mean": np.array(
                                                    ann_mean)}

    return obs_data


def write_meas_file(stream_volume_averages, im_stream_volume_averages, meas_file):
    fid = open(meas_file, 'w')
    gages = stream_volume_averages.keys()
    im_gages = im_stream_volume_averages.keys()
    gage_order = []
    empty_gages = []
    data_time = {}
    for gage in gages:
        if gage in im_gages:
            if len(im_stream_volume_averages[gage]['annual_mean']) > 0:
                annual_flow = im_stream_volume_averages[gage]['annual_mean'][:, 1]
                mon_flow = im_stream_volume_averages[gage]['monthly_mean'][:, 2]
                num_of_meas = len(np.where(np.logical_not(np.isnan(annual_flow)))[0])
                year_time_index = []
                year_month_time_index = []
                i = 0
                msg = "$ " + "SBASINy_" + str(gage) + " " + "% " + str(num_of_meas) + " # Annual unimpaired flow From " \
                                                                                      "BCM" + \
                      "\n"
                fid.write(msg)
                msg = "* SUBBASIN_ID" + " % " + str(gage) + " # --" + "\n"
                fid.write(msg)
                for fl in annual_flow:
                    if not np.isnan(fl):
                        fid.write(str(fl))
                        fid.write("\n")
                        year_time_index.append(im_stream_volume_averages[gage]['annual_mean'][i, 0])
                    i = i + 1
                i = 0
                num_of_meas = len(np.where(np.logical_not(np.isnan(mon_flow)))[0])
                msg = "$ " + "SBASINm_" + str(gage) + " " + "% " + str(num_of_meas) + " # Monthly Unimpaired flow From " \
                                                                                      "BCM" + "\n"
                fid.write(msg)
                msg = "* SUBBASIN_ID" + " % " + str(gage) + " # --" + "\n"
                fid.write(msg)
                for fl in mon_flow:
                    if not np.isnan(fl):
                        fid.write(str(fl))
                        fid.write("\n")
                        yy = im_stream_volume_averages[gage]['monthly_mean'][i, 0]
                        mm = im_stream_volume_averages[gage]['monthly_mean'][i, 1]
                        year_month_time_index.append([yy, mm])
                    i = i + 1
                gage_order.append(gage)
            else:
                empty_gages.append(gage)
        else:
            if len(stream_volume_averages[gage]['annual_mean']) > 0:
                annual_flow = stream_volume_averages[gage]['annual_mean'][:, 1]
                mon_flow = stream_volume_averages[gage]['monthly_mean'][:, 2]
                num_of_meas = len(np.where(np.logical_not(np.isnan(annual_flow)))[0])
                year_time_index = []
                year_month_time_index = []
                i = 0
                msg = "$ " + "SBASINy_" + str(gage) + " " + "% " + str(
                    num_of_meas) + " # Annual NWIS STREAM FLOW" + "\n"
                fid.write(msg)
                msg = "* SUBBASIN_ID " + " % " + str(gage) + " # --" + "\n"
                fid.write(msg)
                for fl in annual_flow:
                    if not np.isnan(fl):
                        fid.write(str(fl))
                        fid.write("\n")
                        year_time_index.append(stream_volume_averages[gage]['annual_mean'][i, 0])
                    i = i + 1

                i = 0
                num_of_meas = len(np.where(np.logical_not(np.isnan(mon_flow)))[0])
                msg = "$ " + "SBASINm_" + str(gage) + " " + "% " + str(
                    num_of_meas) + " # Monthly NWIS STREAM FLOW" + "\n"
                fid.write(msg)
                msg = "* SUBBASIN_ID" + " % " + str(gage) + " # --" + "\n"
                fid.write(msg)
                for fl in mon_flow:
                    if not np.isnan(fl):
                        fid.write(str(fl))
                        fid.write("\n")
                        yy = stream_volume_averages[gage]['monthly_mean'][i, 0]
                        mm = stream_volume_averages[gage]['monthly_mean'][i, 1]
                        year_month_time_index.append([yy, mm])
                    i = i + 1

                gage_order.append(gage)
            else:
                empty_gages.append(gage)

        data_time[gage] = {"annual_t_index": year_time_index, "monthly_t_index": year_month_time_index}
    fid.close()
    return empty_gages, gage_order, data_time


if __name__ == "__main__":

    ## read daily strean volumes and compute monthly averages
    sv_file = r"D:\Workspace\projects\RussianRiver\calibration\Unimpaired_Stream_Volumes.xlsx"
    xl = pd.ExcelFile(sv_file)
    df_unimp = xl.parse("daily_cfs")
    nwis_file = r"D:\Workspace\projects\RussianRiver\Data\StreamGuage\sf_daily"
    gages_shape_file = r"D:\Workspace\projects\RussianRiver\Data\gis\model_gages.shp"
    att_table = shp.get_attribute_table(gages_shape_file)
    if False:
        read_nwis_gages(nwis_file)
    else:
        gage_flow = np.load("nwis_gage_data.npy")
        gage_flow = gage_flow.all()  # [date, flow, approves] cfs

    start_date = datetime.datetime(year=1990, month=1, day=1)
    end_date = datetime.datetime(year=2015, month=12, day=31)
    stream_volume_averages = compute_stream_volume_average(df_unimp, gage_flow, start_date, end_date, att_table)
    im_stream_volume_averages = compute_imp_stream_volume_average(df_unimp, gage_flow, start_date, end_date, att_table)
    observations = dict()
    observations['stream_volume_averages'] = stream_volume_averages
    observations['im_stream_volume_averages'] = im_stream_volume_averages
    np.save('obs_stream_volume.npy', observations)
    meas_file = r"str_volume.meas"
    # The format of the outis as follows : [annual flow and monthly flow for gage i]
    empty_gages, gage_order, data_time = write_meas_file(stream_volume_averages, im_stream_volume_averages, meas_file)
    np.save("stream_volume_times.npy", data_time)
    np.save("gage_order.npy", gage_order)

    ### ************** Calibration Setting **************************
    ### step (1): Prepare names for parameters to calibrate
    para = []
    for i in range(21 * 12):  # 20 basin
        para.append(("radj_fc" + str(i)))

    cal_proj = calibration.Calibration()
    cal_proj.control.MParam.filename = 'str_vol.tpl'
    cal_proj.control.MParam.param_data = para
    # setup the limits and initial values
    param_data = cal_proj.control.MParam.param_data
    param_data['par_val1'].loc[0:] = 1.0  # dday_intcp
    param_data['par_lbnd'].loc[0:] = 0.1  # dday_intcp
    param_data['par_ubnd'].loc[0:] = 2.0  # dday_intcp
    param_data['par_trans'] = 'none'

    cal_proj.control.MParam.write_file()

    ### step (2): prepare observations

    obs_dict = read_obs_file(meas_file)
    cal_proj.control.MObser.obs_data = obs_dict['obs_names']
    cal_proj.control.MObser.filename = 'str_vol.ins'
    cal_proj.control.MObser.obs_data['obs_val'] = obs_dict['obs_values']
    cal_proj.control.MObser.write_ins_file()

    cal_proj.control.filename = "str_vol.pst"
    cal_proj.control.INFLE = "input_str_vol.dat"
    cal_proj.control.OUTFLE = "output_str_vol.dat"

    # model info
    cal_proj.model_python_fn = r"model_Stream_volumes.py"
    cal_proj.generate_model_batch_file('runmodel_str_vol.bat')
    cal_proj.control.write()

    pass

# plot







