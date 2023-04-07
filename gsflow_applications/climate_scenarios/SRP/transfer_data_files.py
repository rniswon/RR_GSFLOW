import glob
import shutil
import os


def  copyfile(extension, exclude):
    for f in glob.glob(OPJ(input_folder, '*.{}'.format(extension))):
        outfile = OPJ(extfile_folder, os.path.basename(f))
        if not os.path.isfile(outfile) and not os.path.basename(f) in exclude:
            print(outfile)
            shutil.copy(f, outfile)


OPJ = os.path.join
thisFolder = os.getcwd()
transfer_srp = False
transfer_rr = True

if transfer_rr:
    #####################################################################################
    # Russian River
    root = os.path.sep.join(thisFolder.split(os.path.sep)[:-4])
    # set the folder for calibrated model input files
    input_folder = OPJ(root, 'model_archive', 'model', 'external_files')
    # set the model folder for the calibrated model
    source_model = OPJ(root, 'model_archive', 'model', 'model1', 'SRPHM_full')
    # set the folder for the new model
    extfile_folder = OPJ(root, 'RR_GSFLOW', 'gsflow_applications', 'climate_scenarios', 'SRP', 'external_files')
    copyfile('txt', '')
    copyfile('dat', 'Climate_stresses_update_1947_2018.dat')

if transfer_srp:
    #####################################################################################
    # SRPHM
    root = os.path.sep.join(thisFolder.split(os.path.sep)[:-4])
    # set the folder for calibrated model input files
    input_folder = OPJ(root, 'model_archive', 'model', 'external_files')
    # set the model folder for the calibrated model
    source_model = OPJ(root, 'model_archive', 'model', 'model1', 'SRPHM_full')
    # set the folder for the new model
    extfile_folder = OPJ(root, 'RR_GSFLOW', 'gsflow_applications', 'climate_scenarios', 'SRP', 'external_files')
    copyfile('txt', ['none'])
    copyfile('dat', ['Climate_stresses_update_1947_2018.dat', 'Climate_stresses.dat'])
