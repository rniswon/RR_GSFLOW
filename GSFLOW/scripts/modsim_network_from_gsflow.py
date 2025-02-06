# # example for russian river (loading entire model)
# # https://github.com/pygsflow/pygsflow/blob/develop/examples/pygsflow_MODSIM_stream_vectors.ipynb
#
# # settings
# import os
# import gsflow
# from gsflow.modsim import Modsim
# from gsflow.modflow import Modflow, ModflowAg
# import flopy as fp
#
# # set paths
# script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
# repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace
# model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20220815_05")
# modsim_network_ws = os.path.join(repo_ws, "MODSIM")
#
#
# # set coordinate system offset of bottom left corner of model grid
# xoff = 465900
# yoff = 4238400
#
# # set epsg
# epsg = 26910
#
# # create empty modflow object and load individual package files
# gsf = gsflow.GsflowModel.load_from_file(os.path.join(model_ws, "windows", "gsflow_rr.control"))
#
# # set grid offsets and epsg code
# gsf.mf.modelgrid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)
#
# # create modsim object and write shapefile
# modsim = gsflow.modsim.Modsim(gsf)
# modsim_shp_file = os.path.join(modsim_network_ws, "modsim_network_20220815_05.shp")
# modsim.write_modsim_shapefile(modsim_shp_file, nearest=False, flag_spillway="elev", flag_ag_diversion=True)

# settings
import gsflow
import flopy
import os

# set file paths
#model_ws = os.path.join(".", "input")
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20220815_05")
name_file_ws = os.path.join(model_ws, "windows")
name_file = os.path.join(model_ws, "windows", "rr_tr.nam")
modsim_network_ws = os.path.join(repo_ws, "MODSIM")
modsim_shp_file = os.path.join(modsim_network_ws, "modsim_network_20220815_05.shp")


# set coordinate system offset of bottom left corner of model grid
xll = 465900
yll = 4238400

# load modflow
ml = gsflow.modflow.Modflow.load(
    name_file,
    model_ws=name_file_ws,
    load_only=["bas6", "dis", "sfr", "lak", "ag"]
)
ml.modelgrid.set_coord_info(xll, yll, angrot=0)

# create modsim shapefile
topo = gsflow.modsim.Modsim(ml)
topo.write_modsim_shapefile(
    modsim_shp_file,
    epsg=26910,
    flag_spillway="elev",
    nearest=False,
    flag_ag_diversion=True
)



