import os, sys
import pandas as pd
sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy" )
sys.path.insert(0, r"D:\Workspace\Codes\pygsflow" )
import uzf_utils
import sfr_utils
import upw_utils
import lak_utils
import output_utils
#from gsflow.utils.vtk import Gsflowvtk, Mfvtk
import flopy

# ----------------------------------------------
# info
# ----------------------------------------------
# this class allows to pass all parameters in concise manner
def run(input_file, real_no):
    class Sim():
        pass
    Sim.name_file = r".\mf_dataset\rr_ss.nam"
    Sim.input_file = input_file
    Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
    Sim.gage_file = r".\misc_files\gage_hru.csv"
    Sim.gage_measurement_file = r".\misc_files\gage_steady_state.csv"
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
    os.chdir(r".\mf_dataset")
    os.system(r'run_gsflow.bat')
    os.chdir(base_folder)

    # ----------------------------------------------
    # Generate outputfile
    # ----------------------------------------------
    output_utils.generate_output_file_ss(Sim)
    if 0:
        try:
            output_utils.generate_output_file_ss(Sim)
        except:
            print("******* Fail**********")




if __name__ == '__main__':

    run(input_file= 'input_param.csv', real_no=0)
