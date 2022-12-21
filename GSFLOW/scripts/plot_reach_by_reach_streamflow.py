# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import flopy
from flopy.utils.sfroutputfile import SfrFile
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp



# ---- Set workspaces, files, and constants -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))           # script workspace
model_ws = os.path.join(script_ws, "..", "scratch", "20221205_02", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")        # model workspace
results_ws = os.path.join(model_ws, "..", "results")      # results workspace

# set workspaces for runs to be compared
model_ws_run_01 = os.path.join(script_ws, "..", "scratch", "20221205_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")
model_ws_run_02 = os.path.join(script_ws, "..", "scratch", "20221205_02", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")
results_ws_compare = os.path.join(script_ws, "script_outputs", "plot_reach_by_reach_streamflow_compare")      # results workspace

# set file names
mf_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")      # name file
sfr_out_file = os.path.join(model_ws, "modflow", "output", "rr_tr.sfr.out")     # set file name for sfr.out
sfr_out_shp_file = os.path.join(results_ws, "plots", "reach_by_reach_streamflow", "sfr_out_20221205_02_sp192_ts31.shp")     # set file name for shapefile
sfr_out_csv_file = os.path.join(results_ws, "tables", "sfr_out_20221205_02_sp192_ts31.csv")    # set file name for csv file

# set file names for runs to be compared
mf_name_01_file = os.path.join(model_ws_run_01, "windows", "rr_tr.nam")      # name file
mf_name_02_file = os.path.join(model_ws_run_02, "windows", "rr_tr.nam")      # name file
sfr_out_01_file = os.path.join(model_ws_run_01, "modflow", "output", "rr_tr.sfr.out")
sfr_out_02_file = os.path.join(model_ws_run_02, "modflow", "output", "rr_tr.sfr.out")
sfr_out_shp_compare_file = os.path.join(results_ws_compare, "sfr_out_20221205_01_minus_20221205_02_sp192_ts31.shp")     # set file name for shapefile
sfr_out_csv_compare_file = os.path.join(results_ws_compare, "sfr_out_20221205_01_minus_20221205_02_sp192_ts31.csv")    # set file name for csv file

# set step and stress period which you want to plot (as a tuple)
sp = 192
ts = 31
kstpkper = (ts-1, sp-1)

# set script options
plot_type = "compare_runs"     # options: "one_run", "compare_runs"

if plot_type == "one_run":

    # make results folders if they don't exist
    if not (os.path.isdir(results_ws)):
        os.mkdir(results_ws)
    if not (os.path.isdir(os.path.join(results_ws, "plots"))):
        os.mkdir(os.path.join(results_ws, "plots"))
    if not (os.path.isdir(os.path.join(results_ws, "plots", "reach_by_reach_streamflow"))):
        os.mkdir(os.path.join(results_ws, "plots", "reach_by_reach_streamflow"))
    if not (os.path.isdir(os.path.join(results_ws, "tables"))):
        os.mkdir(os.path.join(results_ws, "tables"))

elif plot_type == "compare_runs":

    # make results folder if it doesn't exist
    if not (os.path.isdir(results_ws_compare)):
        os.mkdir(results_ws_compare)




# ---- Define function -------------------------------------------####

def plot_reach_by_reach_streamflow(mf_name_file, sfr_out_file, kstpkper, sfr_out_shp_file, sfr_out_csv_file):

    # read in mf
    mf = flopy.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    verbose=True, forgive=False, version="mfnwt",
                                    load_only=["BAS6", "DIS", "SFR"])

    # get model grid
    grid = mf.modelgrid
    xoff = 465900.0
    yoff = 4238400
    epsg = 26910
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)

    # read in sfr output file
    sfr_out = SfrFile(sfr_out_file)
    sfr_out_df = sfr_out.get_dataframe()

    # select desired kstpkper
    sfr_out_df = sfr_out_df[sfr_out_df['kstpkper'] == kstpkper]

    # create and export shapefile
    reach_info = []
    reach_geom = []
    for index, reach in sfr_out_df.iterrows():
        this_reach_df = sfr_out_df[(sfr_out_df['i'] == reach['i']) & (sfr_out_df['j'] == reach['j'])]
        reach_info.append(pd.DataFrame(this_reach_df))
        row = reach['i']
        col = reach['j']
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        reach_geom.append(Point(center[0], center[1]))
    reach_info = pd.concat(reach_info)
    reach_info = reach_info.to_records()
    recarray2shp(reach_info, geoms=reach_geom, shpname=sfr_out_shp_file, epsg=grid.epsg)


    # export table
    sfr_out_df.to_csv(sfr_out_csv_file, index=False)






def compare_reach_by_reach_streamflow(mf_name_01_file, mf_name_02_file, sfr_out_01_file, sfr_out_02_file,
                                      kstpkper, sfr_out_shp_compare_file, sfr_out_csv_compare_file):

    # read in mf
    mf = flopy.modflow.Modflow.load(os.path.basename(mf_name_01_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_01_file)),
                                    verbose=True, forgive=False, version="mfnwt",
                                    load_only=["BAS6", "DIS", "SFR"])

    # get model grid
    grid = mf.modelgrid
    xoff = 465900.0
    yoff = 4238400
    epsg = 26910
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)

    # read in sfr output files
    sfr_out_01 = SfrFile(sfr_out_01_file)
    sfr_out_02 = SfrFile(sfr_out_02_file)
    sfr_out_df_01 = sfr_out_01.get_dataframe()
    sfr_out_df_02 = sfr_out_02.get_dataframe()

    # select desired kstpkpers
    sfr_out_df_01 = sfr_out_df_01[sfr_out_df_01['kstpkper'] == kstpkper]
    sfr_out_df_02 = sfr_out_df_02[sfr_out_df_02['kstpkper'] == kstpkper]

    # read in sfr output files
    sfr_out_df = sfr_out_df_01.copy()
    sfr_out_df['Qaquifer'] = sfr_out_df_02['Qaquifer'] - sfr_out_df_01['Qaquifer']
    sfr_out_df['Qin'] = sfr_out_df_02['Qin'] - sfr_out_df_01['Qin']
    sfr_out_df['Qout'] = sfr_out_df_02['Qout'] - sfr_out_df_01['Qout']
    sfr_out_df['Qovr'] = sfr_out_df_02['Qovr'] - sfr_out_df_01['Qovr']
    sfr_out_df['Qprecip'] = sfr_out_df_02['Qprecip'] - sfr_out_df_01['Qprecip']
    sfr_out_df['Qet'] = sfr_out_df_02['Qet'] - sfr_out_df_01['Qet']

    # create and export shapefile
    reach_info = []
    reach_geom = []
    for index, reach in sfr_out_df.iterrows():
        this_reach_df = sfr_out_df[(sfr_out_df['i'] == reach['i']) & (sfr_out_df['j'] == reach['j'])]
        reach_info.append(pd.DataFrame(this_reach_df))
        row = reach['i']
        col = reach['j']
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        reach_geom.append(Point(center[0], center[1]))
    reach_info = pd.concat(reach_info)
    reach_info = reach_info.to_records()
    recarray2shp(reach_info, geoms=reach_geom, shpname=sfr_out_shp_compare_file, epsg=grid.epsg)

    # export table
    sfr_out_df.to_csv(sfr_out_csv_compare_file, index=False)





# ---- Run function -------------------------------------------####

# plot for one run
if plot_type == "one_run":
    plot_reach_by_reach_streamflow(mf_name_file, sfr_out_file, kstpkper, sfr_out_shp_file, sfr_out_csv_file)

# compare two runs
if plot_type == "compare_runs":
    compare_reach_by_reach_streamflow(mf_name_01_file, mf_name_02_file, sfr_out_01_file, sfr_out_02_file,
                                      kstpkper, sfr_out_shp_compare_file, sfr_out_csv_compare_file)