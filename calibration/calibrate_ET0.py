from pest import calibration
import pandas as pd
import numpy as np

def read_obs_file(fn):
    fid = open(fn,'r')
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
        if marker == '#': # comment
            pass
        elif marker == '$': # measurement name
            meas_base_name = line.strip().split()[1]
            # remove any comments
            line = line.split("#")
            line = line[0]
            num_of_obs = int(line.strip().split('%')[1])

            for n in range(num_of_obs):
                obs_names.append((meas_base_name+ "_"+str(n)))

        elif marker == "*":
            element_type = line.strip().split()[1]
            # remove any comments
            line = line.split("#")
            line = line[0]
            element_id = int(line.strip().split('%')[1])

        else: # read values
            obs_values.append(float(line.strip()))
            obs_loc_type.append(element_type)
            obs_loc_id.append(element_id)
    obs_info['obs_values'] = obs_values
    obs_info['obs_names'] = obs_names
    obs_info['obs_loc_type'] = obs_loc_type
    obs_info['obs_loc_id'] = obs_loc_id
    return obs_info

def compute_monthly_aver(df):
    # average
    mon= [ts.month for ts in df['Date']]
    mon = np.array(mon)
    et_av = []
    for m in range(1, 13, 1):
        mask = mon == m
        curr_et = df['ET'].values[mask]
        et_av.append(np.mean(curr_et))

    return np.array(et_av)


if __name__ == "__main__":

    ## read daily ET and compute monthly averages
    et_file = r"D:\Workspace\projects\RussianRiver\Climate_data\ET0_data_filtered.xlsx"
    xl = pd.ExcelFile(et_file)
    df_106 = xl.parse("106")
    df_51 = xl.parse("51")

    ET106 = compute_monthly_aver(df_106)
    ET51 = compute_monthly_aver(df_51)



        ### ************** Calibration Setting **************************
    ### step (1): Prepare names for parameters to calibrate
    para = []
    for i in range(1,13):
        para.append(("jh_cof_" + str(i)))


    cal_proj = calibration.Calibration()
    cal_proj.control.MParam.filename = 'pot_ET.tpl'
    cal_proj.control.MParam.param_data = para
    # setup the limits and initial values
    param_data = cal_proj.control.MParam.param_data
    param_data['par_val1'].loc[0:11] = 0.016 # dday_intcp
    param_data['par_lbnd'].loc[0:11] = 0.005  # dday_intcp
    param_data['par_ubnd'].loc[0:11] = 0.06  # dday_intcp
    param_data['par_trans'] = 'none'

    ## Important Note: check transp_tmax

    cal_proj.control.MParam.write_file()

    ### step (2): prepare observations
    meas_file = r"ET0_ETp.meas"
    obs_dict = read_obs_file(meas_file)
    cal_proj.control.MObser.obs_data = obs_dict['obs_names']
    cal_proj.control.MObser.filename = 'pot_ET.ins'
    cal_proj.control.MObser.obs_data['obs_val'] = obs_dict['obs_values']
    cal_proj.control.MObser.write_ins_file()

    cal_proj.control.filename = "pot_ET.pst"
    cal_proj.control.INFLE = "input_ET.dat"
    cal_proj.control.OUTFLE = "output_ET.dat"

    # model info
    cal_proj.model_python_fn = r"model_pot_ET.py"
    cal_proj.generate_model_batch_file('runmodel_ET.bat')
    cal_proj.control.write()

    pass


















# plot







