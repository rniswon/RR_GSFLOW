import os,sys

import flopy as flopy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyemu
sys.path.insert(0, r'.\pypackages')
#from pest import calibration
"""
This script prepares all work related to PEST in a calibration experiment. This includes the following:
1- Parameter related work
    1-a if Pilot points are used, then the pilot_point_parwork() function will be used to parameters dataframe, pilot point 
        files, and so on
    1-b custom parameter work  Param_nam_parwork()
    1-c all dataframes pertained to each par group will be saved in a dictionary par_dict{}, the key is group name 
    1-d Template file, which is a dataframe saved as csv file

2- Observation related work
    2-a Divide observations into groups based on location, times or types
    2-b for each group cutomized heads_obswork() to process observation, the same function must be used to process model
        predictions
    2-c all dataframes pertained to each obs group will be saved in a dictionary obs_dict{}, the key is group name 
    2-d Instruction files as csv

3- Pest control file work 
4- HTcondor work

"""
def main():

    ## ---- Declarations
    mf_name = r"D:\Models\Yucaipa\kalman_filter3\Kalman_Filter2\main_folder\tran_mf3d\yucaipa.nam"
    pst_name = r"D:\Models\Yucaipa\kalman_filter3\Kalman_Filter2\main_folder\yuc.pst"
    model_runner_script = "model_runner.py"
    model_pst_bat = "model_run_tr.bat"
    input_file = "input_hk.csv"

    hob_template = r"D:\Models\Yucaipa\kalman_filter3\Kalman_Filter2\main_folder\pest_files\yucaipa.hob.out"
    ins_file = r"hob_obs.ins"
    # generate pre-constructed pst
    pst = pyemu.Pst.from_par_obs_names(par_names=['par1'], obs_names=['obs1'])
    tpl_files = []
    ins_files = []

    ## ---- parameter related work
    par_prefix = 'hk'
    pp_dict = kpp_parwork(mf_name, pst_name, prefix = par_prefix)

    # generate template file
    pp_df = pp_dict['pp_df']
    pp_df = pp_df.drop(['tpl_filename', 'pp_filename'], axis=1)
    infile = os.path.join("input_{}.csv".format(par_prefix))
    pp_df.to_csv(infile)
    tpl_file =  "{}_pp.tpl".format(par_prefix)
    write_tpl_from_df(tpl_file, pp_df, header="ptf ~")

    tpl_files.append(tpl_file)
    param_df = pp_df.drop(['name',  'x', 'y', 'zone', 'parval1', 'k', 'i', 'j', 'tpl'], axis = 1)
    param_df['parubnd'] = 2.0
    param_df['parlbnd'] = -2.0
    param_df['parval1'] = 0
    param_df['partrans'] = 'none'
    param_df['pargp'] = 'hk'
    parmdf = pd.DataFrame(columns=pst.parameter_data.columns)
    for key in pst.parameter_data.columns:
        parmdf[key] = param_df[key].values
    pst.parameter_data = parmdf
    #generate instructions

    heads_obswork(hob_template,ins_file,pst )
    ins_files.append(ins_file)

    # Generate bat file to run pest model
    fidw = open(model_pst_bat, 'w')
    cmd = "python " + model_runner_script
    fidw.write(cmd)
    fidw.close()

    # write_control
    pst.model_command = [model_pst_bat]
    pst.input_files = 1
    pst.write(pst_name)
    passs = 1





def heads_obswork(fn, fn_ins, pst):
    """

    :param fn: a template for hob.out output file
    :return:
    """
    hob_out = np.loadtxt(fn, dtype=np.str, skiprows=1)
    sim_obs = hob_out[:,0:2]
    sim_obs = sim_obs.astype('float')
    loc = np.logical_and(sim_obs[:,0]>0, np.logical_not(np.isnan(sim_obs[:,0])))
    obs_names = hob_out[loc,2]
    columns = pst.observation_data.columns
    obs_data = pd.DataFrame({'obsnme': obs_names})
    obs_data['obsval'] = sim_obs[loc,1]
    obs_data['weight'] = 1.0
    obs_data['obgnme'] = 'head'
    pst.observation_data = obs_data
    pst.observation_data.to_csv(fn_ins + '.csv')
    #---------------------------
    delimiter = "$"
    obs_size = 25
    fid = open(fn_ins, 'w')
    fid.write("pif %s\n" % (delimiter))
    obs_names = obs_data['obsnme'].values
    for nm in obs_names:
        fid.write("l1 ")
        fid.write("[{}]".format(nm))
        fid.write("1:{}".format(obs_size))
        fid.write("\n")

    fid.close()


def write_tpl_from_df(fn, df, header):

    fid = open(fn, 'w')
    fid.write(header)
    fid.write("\n")
    fid.close()
    df.to_csv(fn,  mode='a')

def kpp_parwork(mf_name = None, pst_name = None, prefix = 'par1'):
    """
    Custom function to scale parameter field
    :param mf_name:
    :param pst_name:
    :return:
    """
    pp_dict = {}
    # Model To be used
    m = flopy.modflow.Modflow.load(mf_name, load_only=['DIS', 'BAS6', 'UPW'])
    working_dir = os.path.dirname(pst_name)
    prefix_dict = {1: ["hk1"], 2: ["hk2"], 3: ["hk3"]}

    # compute pilot points in active zone in three layers
    df_pp = pyemu.gw_utils.setup_pilotpoints_grid(ml=m, prefix_dict=prefix_dict,
                                                  pp_dir=working_dir,
                                                  tpl_dir=working_dir,
                                                  every_n_cell=10)
    # Becuase we use pilot points as a scaling parameters, we need only one layer
    xy = df_pp[['x', 'y']].values
    unique_rows, index = np.unique(xy, return_index=True, axis=0)
    df2 = pd.DataFrame(np.zeros((len(unique_rows), len(df_pp.columns))), columns=df_pp.columns)
    df2['x'] = unique_rows[:, 0]
    df2['y'] = unique_rows[:, 1]
    for col in df_pp.columns:
        if not col in ['x', 'y']:
            df2[col] = df_pp[col].values[index]

    # correct pp name
    for i in range(len(df2)):
        ppname = "pp_" + str(i)
        df2.loc[i, 'name'] = ppname
        df2.loc[i, 'parnme'] = "{}_".format(prefix) + str(i)
        df2.loc[i, 'tpl'] = '~    {}{}    ~'.format(prefix,i)
    pp_file = os.path.join(working_dir, "{}pp.dat".format(prefix))
    pp_dict['pp_file'] = pp_file
    pp_dict['pp_df'] = df2
    ## Geostatistics
    v = pyemu.geostats.ExpVario(contribution=1.0, a=4000)
    gs = pyemu.geostats.GeoStruct(variograms=v, nugget=0.0)
    ax = gs.plot()
    ax.grid()
    ax.set_ylim(0, 2.0)
    if 0:
        ok = pyemu.geostats.OrdinaryKrige(gs, df2)
        df = ok.calc_factors_grid(m.sr, var_filename=pst_name.replace(".pst", ".var.ref"), minpts_interp=1,
                                  maxpts_interp=10)
        arr_var = np.loadtxt(pst_name.replace(".pst", ".var.ref"))
        ax = plt.subplot(111, aspect="equal")
        p = ax.imshow(arr_var, extent=m.sr.get_extent(), alpha=0.25)
        plt.colorbar(p)
        ax.scatter(df2.x, df2.y, marker='.', s=4, color='r')
    if 0:
        ok.to_grid_factors_file(pp_file + ".fac")
    pp_dict['fac_file'] = pp_file + ".fac"

    # Testing Only: generate random values
    # df2.loc[:, "parval1"] = np.random.randn(df2.shape[0])

    # save a pilot points file
    pyemu.gw_utils.write_pp_file(pp_file, df2)

    # Testing Only interpolate the pilot point values to the grid
   # hk_arr = pyemu.gw_utils.fac2real(pp_file, factors_file=pp_file + ".fac", out_file=None)

    return pp_dict







pyemu.Pst.from_par_obs_names
pass


if __name__ == "__main__":

    main()