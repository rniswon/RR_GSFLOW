import os, sys
import pandas as pd
#sys.path.insert(0, r"C:\work\Russian_River\py_pkgs" )
sys.path.insert(0, r"C:\work\code" )

import uzf_utils
import sfr_utils
import upw_utils
import lak_utils
import output_utils
#from gsflow.utils.vtk import Gsflowvtk, Mfvtk
import flopy
import numpy as np

# ----------------------------------------------
# info
# ----------------------------------------------
# this class allows to pass all parameters in concise manner
def run(input_file = None, real_no=-999, output_file = None):
    """

    :param input_file: must be a csv file with pst header
    :param real_no: realization id. if negative means no monte carlo is made
    :param output_file: must be csv file
    :return:
    """
    class Sim():
        pass
    Sim.name_file = r".\mf_dataset\rr_ss.nam"
    Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
    Sim.gage_file = r".\misc_files\gage_hru.csv"
    Sim.gage_measurement_file = r".\misc_files\gage_steady_state.csv"

    if not(input_file is None):
        Sim.input_file = input_file
    else:
        Sim.input_file = 'input_param.csv'

    if real_no < 0:
        if not(output_file is None):
            # use the name provided
            Sim.output_file = output_file
        else:
            Sim.output_file = r"model_output.csv"

    else: # monte Carlo
        if not(output_file is None):
            # use the name provided
            Sim.output_file = os.path.basename(output_file) + "_{}.csv".format(real_no)
        else:
            Sim.output_file = r"model_output_{}.csv".format(real_no)


    # ----------------------------------------------
    # Prepare ...
    # ----------------------------------------------

    # Always remove model output


    # ----------------------------------------------
    # Change model
    # ----------------------------------------------
    # load the model
    Sim.mf = flopy.modflow.Modflow.load(os.path.basename(Sim.name_file), model_ws= os.path.dirname(Sim.name_file),
                                        verbose = True, forgive = False)

    # Lake information
    if False:
        lak_utils.change_lak_ss(Sim)

    # UPW information
    upw_utils.change_upw_ss(Sim)

    # UZF information
    uzf_utils.change_uzf_ss(Sim)

    # SFR information
    sfr_utils.change_sfr_ss(Sim)

    # ----------------------------------------------
    # Run the model
    # ----------------------------------------------
    #Sim.mf.lak.write_file()
    Sim.mf.upw.write_file()
    Sim.mf.uzf.write_file()
    Sim.mf.sfr.write_file()
    base_folder = os.getcwd()
    print("change param....")
    os.chdir(r".\mf_dataset")
    os.system(r'run_gsflow.bat')
    os.chdir(base_folder)
    print("finish model run")

    # ----------------------------------------------
    # Generate outputfile
    # ----------------------------------------------


    try:
        output_utils.generate_output_file_ss(Sim)
    except:
        print("******* Fail**********")


def run_simple_in_out(in_fn, out_fn, csv_in, csv_out):
    """

    :param in_fn: simple columns of input parameters
    :param out_fn: simple column of output parameters
    csv_in: is a template csv file that we use to run the model. Column read from in_fn is isnerted in parval in this csv
    csv_out same but for output

    :return:
    """
    try:
        os.remove(out_fn)
    except:
        pass
    df_in = pd.read_csv(csv_in)
    vals = np.loadtxt(in_fn)
    df_in['parval1'] = vals
    df_in.to_csv(csv_in,  index=None)
    print("Enter run....")
    run(input_file= csv_in, output_file = csv_out)

    df_out = pd.read_csv(csv_out)
    outvals = df_out['simval'].values
    np.savetxt(out_fn, outvals, fmt="%.3f")
    print("Write output....")


if __name__ == '__main__':

    run(input_file= 'input_param.csv')
    print("Start model run....")
    #run_simple_in_out('input_param.dat', 'model_output.dat', 'input_param.csv', 'model_output.csv')
    print("End model run....")
    pass
