import os, sys
from pyprms import prms_py
import matplotlib.pyplot as plt


cname = "D:\Workspace\projects\RussianRiver\RR_GSFLOW\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()

if True:
    lapsez= prms.prms_parameters['Parameters']['hru_tlaps'][4]
    #mask = (lapsez == 6) # potter
    mask = prms.prms_parameters['Parameters']['hru_elev'][4] >= 600
    lapsez[mask] = 7

    x = 1


folder = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW\windows"
fn_param = os.path.join(folder,"prms_rr_temp.param")
prms.write_param_file(fn_param)

x = 1

#