import os, sys


control_file = r"D:\Workspace\projects\archive\archive\model\prms\rsj_prms_sub_cfs.control"
sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")
import gsflow
from gsflow.utils.vtk import Gsflowvtk
if True:
    Gsflowvtk.gsflow_to_vtk(control_file=control_file, mf_pkg = ['DIS', 'BAS6', 'SFR', 'UPW', 'UZF'])

gs = gsflow.GsflowModel.load_from_file(control_file = control_file, mf_load_only = ['DIS', 'BAS6', 'SFR'],
                                       modflow_only=True )

xx = 1