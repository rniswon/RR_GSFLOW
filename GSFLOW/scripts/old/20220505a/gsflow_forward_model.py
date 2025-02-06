# ----------------------------------------------
# Setup
# ----------------------------------------------
run_cluster = False

if run_cluster == True:

    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "Miniconda3")

    import pandas as pd
    import numpy as np
    import gsflow
    import flopy
    import time

    import uzf_utils
    import sfr_utils
    import upw_utils
    import lak_utils
    import well_utils
    import output_utils
    import prms_utils
    import ghb_utils


else:

    import os, sys
    import pandas as pd
    import numpy as np
    import gsflow
    import flopy
    import time

    import uzf_utils
    import sfr_utils
    import upw_utils
    import lak_utils
    import well_utils
    import output_utils
    import prms_utils
    import ghb_utils


# ----------------------------------------------
# Settings
# ----------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")





# ----------------------------------------------
# Define run function
# ----------------------------------------------

# this class allows to pass all parameters in concise manner
def run(input_file = None, real_no=-999, output_file = None):
    """

    :param input_file: must be a csv file with pst header
    :param real_no: realization id. if negative means no monte carlo is made
    :param output_file: must be csv file
    :return:
    """

    # ----------------------------------------------
    # Set file names and paths
    # ----------------------------------------------
    class Sim():
        pass
    Sim.repo_ws = repo_ws
    Sim.script_ws = script_ws
    Sim.name_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "windows", "rr_tr.nam")
    Sim.prms_control = os.path.join(repo_ws, "GSFLOW", "worker_dir", 'windows', 'prms_rr.control')
    Sim.hru_shp_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "hru_shp.csv")
    Sim.gage_hru_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", 'gage_hru.shp')
    Sim.pest_obs_all = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
    Sim.gage_measurement_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_streamflow.csv")
    Sim.subbasins_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "subbasins.txt")
    Sim.surf_geo_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "surface_geology.txt")
    Sim.grid_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "grid_info.npy")
    Sim.K_zones_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "K_zone_ids_20220318.dat")
    Sim.ghb_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "ghb_hru_20220404.shp")
    Sim.pump_red_file_nonag = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "output", "pumping_reduction.out")
    Sim.pump_red_file_ag = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "output", "pumping_reduction_ag.out")
    Sim.model_output_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "pest", "model_output.csv")
    Sim.modflow_output_folder = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "output")
    Sim.windows_folder = os.path.join(repo_ws, "GSFLOW", "worker_dir", "windows")


    if not(input_file is None):
        Sim.input_file = input_file
    else:
        Sim.input_file = 'input_param.csv'

    if real_no < 0:
        if not(output_file is None):
            Sim.output_file = output_file
        else:
            Sim.output_file = r"model_output.csv"

    else: # monte Carlo
        if not(output_file is None):
            Sim.output_file = os.path.basename(output_file) + "_{}.csv".format(real_no)
        else:
            Sim.output_file = r"model_output_{}.csv".format(real_no)


    # ----------------------------------------------
    # Set constants
    # ----------------------------------------------

    # set start and end dates of modeling period
    Sim.start_date = "01-01-1990"
    Sim.end_date = "12-31-2015"



    # ----------------------------------------------
    # Prepare
    # ----------------------------------------------

    # Always remove model output



    # ----------------------------------------------
    # Update parameters
    # ----------------------------------------------

    # load the models
    Sim.mf = flopy.modflow.Modflow.load(os.path.basename(Sim.name_file), model_ws= os.path.dirname(Sim.name_file),
                                        verbose = True, forgive = False, version="mfnwt",
                                        load_only=["BAS6", "DIS", "UPW", "UZF", "LAK", "SFR", "WEL", "GHB"])
    Sim.gs = gsflow.GsflowModel.load_from_file(control_file=Sim.prms_control)


    # UPW
    # update: upw_ks, upw_vka, upw_ss, upw_sy
    upw_utils.change_upw_tr(Sim)

    # UZF
    # update: uzf_extdp, uzf_surfdep, uzf_surfk, uzf_vks
    uzf_utils.change_uzf_tr(Sim)

    # LAK
    # update: lak_cd
    lak_utils.change_lak_tr(Sim)

    # SFR
    # update: sfr_ks
    sfr_utils.change_sfr_tr(Sim)

    # Well
    # update: well_rubber_dam
    # TODO: do we need this in the transient model?  if not, remove the param from the input param file, and remove the wells from the well file (if they're in there)
    #well_utils.change_well_tr(Sim)

    # GHB
    # update: ghb_bhead
    ghb_utils.change_ghb_tr(Sim)

    # PRMS
    # update: prms_jh_coef, prms_sat_threshold, prms_slowcoef_lin, prms_slowcoef_sq,
    #         prms_soil_moist_max,  prms_soil_rechr_max_frac, prms_ssr2gw_rate
    prms_utils.change_prms_param(Sim)

    # change file paths for export of updated model input files
    # TODO: figure out why these files aren't being written to these file paths
    Sim.mf.upw.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.upw")
    Sim.mf.uzf.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.uzf")
    Sim.mf.lak.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.lak")
    Sim.mf.sfr.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.sfr")
    Sim.mf.wel.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.wel")
    Sim.mf.ghb.fn_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "modflow", "input", "rr_tr.ghb")


    # write updated parameters
    Sim.mf.upw.write_file()
    Sim.mf.uzf.write_file()
    Sim.mf.lak.write_file()  # TODO: check whether I need to do the same work-around in lake_utils that I did for the ss model
    Sim.mf.sfr.write_file()
    #Sim.mf.wel.write_file()  # TODO: do we need this in the transient model?
    Sim.mf.ghb.write_file()
    Sim.gs.prms.parameters.write()

    print("Updated parameters")



    # ----------------------------------------------
    # Run the model
    # ----------------------------------------------

    base_folder = os.getcwd()
    windows_folder = Sim.windows_folder
    os.chdir(windows_folder)
    print("Starting model run")
    os.system(r'run.bat')
    os.chdir(base_folder)
    print("Finished model run")


    # ----------------------------------------------
    # Generate output file
    # ----------------------------------------------

    try:
        output_utils.generate_output_file_tr(Sim)
        print("Generated output file")
    except:
        print("Could not generate output file")




# # ----------------------------------------------
# # Define simple run function
# # ----------------------------------------------
# def run_simple_in_out(in_fn, out_fn, csv_in, csv_out):
#     """
#
#     :param in_fn: simple columns of input parameters
#     :param out_fn: simple column of output parameters
#     csv_in: is a template csv file that we use to run the model. Column read from in_fn is inserted in parval in this csv
#     csv_out same but for output
#
#     :return:
#     """
#     try:
#         os.remove(out_fn)
#     except:
#         pass
#     df_in = pd.read_csv(csv_in)
#     vals = np.loadtxt(in_fn)
#     df_in['parval1'] = vals
#     df_in.to_csv(csv_in,  index=None)
#     print("Enter run....")
#     run(input_file= csv_in, output_file = csv_out)
#
#     df_out = pd.read_csv(csv_out)
#     outvals = df_out['simval'].values
#     np.savetxt(out_fn, outvals, fmt="%.3f")
#     print("Write output....")


# ----------------------------------------------
# Set what to do if entire script is called
# ----------------------------------------------
if __name__ == '__main__':

    time_start = time.time()
    print("Starting model run")

    input_param_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param.csv")
    run(input_file= input_param_file)
    #shutil.copyfile(r"model_output - Copy.csv", "model_output.csv")
    #run_simple_in_out('input_param.dat', 'model_output.dat', 'input_param.csv', 'model_output.csv')

    print("End of model run")
    time_end = time.time()
    seconds_per_hour = 3600
    total_time_hr = (time_end - time_start)/seconds_per_hour
    print("Total run time: ", total_time_hr, "hours")

    pass
