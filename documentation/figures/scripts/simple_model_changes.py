import os
import matplotlib.pyplot as plt
import numpy as np
import geopandas
import pandas as pd
import gsflow
import gis_utils

def read_simulated_streamflow(gs):
    """
    Read PRMS output file
    @param gs:
    @return:
    """
    basename = gs.control.get_values('nsubOutBaseFileName')[0]
    ws = os.path.dirname(gs.control_file)
    fn = os.path.join(ws, basename + "sroff.csv")
    df = pd.read_csv(fn)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # make subbasin id integer
    cols = df.columns
    for col in cols:
        df.rename(columns={col:int(col)}, inplace = True)

    return df



# =========================
# Global Variables
# =========================

# (1) File names
hru_param_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp"
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows"
output_ws = r"D:\Workspace\projects\RussianRiver\Data\gis_from_model"

# (2) Georeferencing
xoff = 465900.0
yoff = 4238400
epsg= 26910
ncol = 253
nrow = 411
# grid = mf.modelgrid
# grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)


# (3) load gsflow
control_file = os.path.join(ws, r"gsflow_rr.control")
gs = gsflow.GsflowModel.load_from_file(control_file=control_file, model_ws=ws, mf_load_only=['DIS', 'BAS6', 'UPW', 'sfr', 'UZF'])
mf = gs.mf

subbasin_id = gs.prms.parameters.get_values("hru_subbasin")

#streamflow in inches
streamflow = read_simulated_streamflow(gs)
for subbasin in streamflow.columns:

    # convert area from acre to m2
    hru_area = gs.prms.parameters.get_values('hru_area') * 4046.86
    nhru = np.sum(subbasin_id==subbasin)
    streamflow[subbasin] = streamflow[subbasin] * hru_area * nhru





xx= 1



