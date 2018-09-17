from pest import calibration

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


if __name__ == "__main__":

    all_params = {'dday_slope':[0.2, 0.7], 'dday_intcp':[-60, 4], 'radj_sppt' : [0.0, 1.0],
                  'radj_wppt':[0.0, 1.0], 'radadj_slope':[0.0, 1.0],
                  'radadj_intcp':[0.0,1.0], 'radmax':[0.0, 1.0], 'ppt_rad_adj':[0.0, 0.5],
                  'tmax_index':[-10, 110], 'tmax_allrain':[0.0,90.0]}
    par_to_calib = {'dday_slope':[0.2, 0.7], 'dday_intcp':[-60, 4], 'tmax_index':[-10, 110]}

    ### ************** Calibration Setting **************************
    ### step (1): Prepare names for parameters to calibrate
    para = []
    for i in range(1,13):
        para.append(("dinctp_" + str(i)))
    for i in range(1,13):
        para.append(("dslope_" + str(i)))

    cal_proj = calibration.Calibration()
    cal_proj.control.MParam.filename = 'solar_rad2.tpl'
    cal_proj.control.MParam.param_data = para
    # setup the limits and initial values
    param_data = cal_proj.control.MParam.param_data
    param_data['par_val1'].loc[0:11] = -2 # dday_intcp
    param_data['par_lbnd'].loc[0:11] = -60  # dday_intcp
    param_data['par_ubnd'].loc[0:11] = 4  # dday_intcp
    param_data['par_val1'].loc[12:] = 0.4  # dday_slope
    param_data['par_lbnd'].loc[12:] = 0.2  # dday_slope
    param_data['par_ubnd'].loc[12:] = 0.7  # dday_slope
    param_data['par_trans'] = 'none'

    cal_proj.control.MParam.write_file()

    ### step (2): prepare observations
    meas_file = r"solar_rad_monthly_aver.meas"
    obs_dict = read_obs_file(meas_file)
    cal_proj.control.MObser.obs_data = obs_dict['obs_names']
    cal_proj.control.MObser.filename = 'solar_rad2.ins'
    cal_proj.control.MObser.obs_data['obs_val'] = obs_dict['obs_values']
    cal_proj.control.MObser.write_ins_file()

    cal_proj.control.filename = "solar_rad2.pst"
    cal_proj.control.INFLE = "input_solar2.dat"
    cal_proj.control.OUTFLE = "output_solar2.dat"

    # model info
    cal_proj.model_python_fn = r"model_solar_radiation.py"
    cal_proj.generate_model_batch_file('runmodel.bat')
    cal_proj.control.write()

    pass


















# plot







