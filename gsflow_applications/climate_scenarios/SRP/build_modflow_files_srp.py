import pandas as pd
import flopy as fp
import os
from datetime import datetime
import numpy as np

'''
__author__ = "Derek Ryter"
__version__ = "01"

Script to build the non-transient files for the SRP climate models.

ARGUMENTS:
    none

REQUIREMENTS:
    hauer_county_totpop_SSPs.shp
        and all associated files
    censuspop.csv: census population of Sonoma and Mendocino counties 2015 - 2020
    county_population_change.csv: file made by future_population.py with columns for year,
        and population and population change relative to 2015 for both counties.
    
OUTPUT:
    srp_climate.nam
    ../external_files/srp_climate.wel
    ../external_files/srp_climate.nwt
    ../external_files/srp_climate.bas
    ../external_files/srp_climate.dis


Some functions are very tailored to SRP, some are more general.

'''

######################################################################
# SRPHM only needs to adjust pumping for the WEL package and
# all wells are in Sonoma County
OPJ = os.path.join
thisFolder = os.getcwd()
root = os.path.sep.join(thisFolder.split(os.path.sep)[:-4])
# set the folder for calibrated model input files
input_folder = OPJ(root, 'model_archive', 'model', 'external_files')
# set the model folder for the calibrated model
source_model = OPJ(root, 'model_archive', 'model', 'model1', 'SRPHM_full')
# set the folder for the new model
ext_folder = OPJ(root, 'RR_GSFLOW', 'gsflow_applications', 'climate_scenarios', 'SRP', 'external_files')
model_folder = OPJ(root, 'RR_GSFLOW', 'gsflow_applications', 'climate_scenarios', 'SRP', 'windows')
model_name = 'srphm_climate'
mod_namefile = 'srphm_climate.nam'
print('loading model...')
m = fp.modflow.Modflow.load('SRPHM_full.nam', model_ws=source_model,
                            version='mfnwt')
wel = m.wel
# create another model to use the new packages
mc = fp.modflow.Modflow(model_ws=model_folder,
                        modelname=model_name,
                        version='mfnwt')

##################################################################
# build the monthly stress periods and DIS file
ar_perlen = []
ar_trans = []
# set the future period of years
ext_years = range(2019, 2101)
print('building new dis package...')
for yr in ext_years:
    for mo in range(1, 12):
        startdate = datetime(yr, mo, 1)
        enddate = datetime(yr, mo + 1, 1)
        delta = enddate - startdate
        ar_perlen.append(delta.days)
        ar_trans.append(False)
    lastdate = datetime(yr + 1, 1, 1)
    delta = lastdate - enddate
    ar_perlen.append(delta.days)
    ar_trans.append(False)
nper = len(ar_perlen)
print('there are {} stress periods in the extended model.'.format(nper))
#tstplist =
dis_new = fp.modflow.ModflowDis(
    mc,
    nlay=m.dis.nlay,
    nrow=m.dis.nrow,
    ncol=m.dis.ncol,
    nper=nper,
    delr=m.dis.delr,
    delc=m.dis.delc,
    top=m.dis.top,
    botm=m.dis.botm,
    perlen=ar_perlen,
    nstp=2,
    steady=ar_trans,
    filenames='../external_files/{}.dis'.format(model_name)
)
# include a couple input files to save time later
#####################
# bas
bas6 = m.bas6
mc.bas6 = bas6
mc.bas6.filenames = '../external_files/{}.bas'.format(model_name)
#####################
# nwt
nwt = fp.modflow.ModflowNwt.load(OPJ(input_folder, 'srphm.nwt'), mc)
mc.nwt.filenames = '../external_files/{}.nwt'.format(model_name)
#####################
# oc
spd = {}
for sp in range(nper):
    spd[sp, 0] = ['save head', 'save budget']
oc = fp.modflow.ModflowOc(mc,
                          filenames='../external_files/{}.oc'.format(model_name),
                          stress_period_data=spd
                          )
#####################
# mult
#mult = fp.modflow.ModflowMlt.load(OPJ(ext_folder, 'srphm_climate.mul'), mc)
#####################
# upw
#upw = fp.modflow.ModflowUpw.load(OPJ(input_folder, 'srphm.upw'), mc)
#mc.upw.filenames='../external_files/{}.upw'.format(model_name)
#####################
# zone
zonedict = {}
for lay in range(1, mc.dis.nlay + 1):
    zarray = np.loadtxt(OPJ(input_folder, 'StorUnit{}.txt'.format(lay)))
    zonedict[lay-1] = zarray
zone = fp.modflow.ModflowZon(mc,
                             zone_dict=zonedict,
                             filenames='../external_files/{}.zon'.format(model_name)
                             )

print('writing the model files...')
mc.write_input()
mc.write_name_file()
#
print('done.')
