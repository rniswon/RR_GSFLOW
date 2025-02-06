import os, sys
from pyprms import prms_py


cname = "D:\Workspace\projects\RussianRiver\gsflow\prms2\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()
if False: #From F to C  # dont run unless you are sure that you want to change units
    prms.prms_parameters['Parameters']['tmin_adj'][4] = (prms.prms_parameters['Parameters']['tmin_adj'][4]-32.0)/1.8
    prms.prms_parameters['Parameters']['tmax_adj'][4] = (prms.prms_parameters['Parameters']['tmax_adj'][4]-32.0)/1.8

if False: #From C to F  # dont run unless you are sure that you want to change units
    prms.prms_parameters['Parameters']['tmin_adj'][4] = (prms.prms_parameters['Parameters']['tmin_adj'][4]*1.8) + 32.0
    prms.prms_parameters['Parameters']['tmax_adj'][4] = (prms.prms_parameters['Parameters']['tmax_adj'][4]*1.8) + 32.0

if False:
    prms.prms_parameters['Parameters']['hru_tsta'][4] = prms.prms_parameters['Parameters']['hru_tsta'][4] - 5

if False:
    prms.prms_parameters['Parameters']['hru_tsta'][4] = prms.prms_parameters['Parameters']['hru_tsta'][4] + 1

if True:
    lapsez= prms.prms_parameters['Parameters']['hru_tlaps'][4]
    #mask = (lapsez == 6) # potter
    mask = prms.prms_parameters['Parameters']['hru_elev'][4] >= 700
    lapsez[mask] = 7

    x = 1


folder = r"D:\Workspace\projects\RussianRiver\gsflow\prms2\input"
fn_param = os.path.join(folder,"prms_rr.param")
prms.write_param_file(fn_param)

x = 1

#