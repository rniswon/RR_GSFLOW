import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import ArrayToShapeFile as ATS
import make_utm_proj as mup
import flopy.export.shapefile_utils
import geopandas
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp


# ---- Settings -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                  # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                        # model workspace
results_ws = os.path.join(model_ws, "..", "results")                                    # results workspace

# set grid cell area
x_len = 300
y_len = 300
grid_cell_area = x_len * y_len
square_m_per_square_km = 1000000


# ---- Read in -------------------------------------------####

# read in ag package
mf_name_file_type = 'rr_tr_heavy.nam'
mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS", "AG"],
                                    verbose=True, forgive=False, version="mfnwt")
#ag = mf_tr.ag

# read in prms param file and get ag_frac and hru_id
gsflow_control = os.path.join(model_ws, 'windows', 'gsflow_rr.control')
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)
ag_frac = gs.prms.parameters.get_values('ag_frac')
hru_id = np.asarray(list(range(1,len(ag_frac) + 1)))




# ---- Calculate irrigated area -------------------------------------------####


# get HRU IDs of irrigated cells for each source type using stress period data from one full year (i.e. stress periods 1-12) - since
# the stress period data repeats for each calendar year
    # make list of HRU_ID_DIVERSION from IRRDIVERSION
    # make list of HRU_ID_WELL from IRRWELL
    # make list of HRU_ID_POND from IRRPOND

# use ag_frac and grid cell area to calculate irrgated area for each grid cell
irrig_area_df = pd.DataFrame({'hru_id': hru_id, 'ag_frac': ag_frac})
irrig_area_df['irrig_area_m2'] = ag_frac * grid_cell_area

# prep
irrdiv_dict = dict(list(mf_tr.ag.irrdiversion.items())[0: 311])
irrwell_dict = dict(list(mf_tr.ag.irrwell.items())[0: 311])
irrpond_dict = dict(list(mf_tr.ag.irrpond.items())[0: 311])
stress_periods = [0,1,2,3,4,5,6,7,8,9,10,11]
div_hru = []
well_hru = []
pond_hru = []


# irrdiv
for key, rec_array in irrdiv_dict.items():

    # get hru id names
    field_names = rec_array.dtype.names
    hru_id_names = [x for x in field_names if 'hru_id' in x]

    # get and store hru_id values
    for hru_id_name in hru_id_names:
        hru_id_val = rec_array[hru_id_name].tolist()
        div_hru = np.append(div_hru, hru_id_val)
    #div_hru = [item for row in div_hru for item in row]
    div_hru = np.asarray(div_hru)
    div_hru = div_hru[div_hru > 0]   # only keep real hru id values
    div_hru = np.unique(div_hru)  # only keep unique values
    div_hru = div_hru + 1 # to match up with hru ids

    # get irrigated area for diversions
    irrig_area_div = irrig_area_df.copy()
    irrig_area_div = irrig_area_div[irrig_area_div['hru_id'].isin(div_hru)]
    irrig_area_div_sum_km = irrig_area_div['irrig_area_m2'].sum() * (1/square_m_per_square_km)


# irrwell
for key, rec_array in irrwell_dict.items():

    # get hru id names
    field_names = rec_array.dtype.names
    hru_id_names = [x for x in field_names if 'hru_id' in x]

    # get and store hru_id values
    for hru_id_name in hru_id_names:
        hru_id_val = rec_array[hru_id_name].tolist()
        well_hru = np.append(well_hru, hru_id_val)
    #well_hru = [item for row in well_hru for item in row]
    well_hru = np.asarray(well_hru)
    well_hru = well_hru[well_hru > 0]  # only keep real hru id values
    well_hru = np.unique(well_hru)  # only keep unique values
    well_hru = well_hru + 1 # to match up with hru ids

    # get irrigated area for wells
    irrig_area_well = irrig_area_df.copy()
    irrig_area_well = irrig_area_well[irrig_area_well['hru_id'].isin(well_hru)]
    irrig_area_well_sum_km = irrig_area_well['irrig_area_m2'].sum() * (1/square_m_per_square_km)



# irrpond
for key, rec_array in irrpond_dict.items():

    # get hru id names
    field_names = rec_array.dtype.names
    hru_id_names = [x for x in field_names if 'hru_id' in x]

    # get and store hru_id values
    for hru_id_name in hru_id_names:
        hru_id_val = rec_array[hru_id_name].tolist()
        pond_hru = np.append(pond_hru, hru_id_val)
    #pond_hru = [item for row in pond_hru for item in row]
    pond_hru = np.asarray(pond_hru)
    pond_hru = pond_hru[pond_hru > 0]  # only keep read hru id values
    pond_hru = np.unique(pond_hru)   # only keep unique values
    pond_hru = pond_hru + 1 # to match up with hru ids

    # get irrigated area for ponds
    irrig_area_pond = irrig_area_df.copy()
    irrig_area_pond = irrig_area_pond[irrig_area_pond['hru_id'].isin(pond_hru)]
    irrig_area_pond_sum_km = irrig_area_pond['irrig_area_m2'].sum() * (1/square_m_per_square_km)


# calculate total irrigated area
irrig_area_total = irrig_area_df.copy()
irrig_hru = np.concatenate((pond_hru, well_hru, div_hru))
irrig_hru = np.unique(irrig_hru)
irrig_area_total = irrig_area_total[irrig_area_total['hru_id'].isin(irrig_hru)]
irrig_area_total_sum_km = irrig_area_total['irrig_area_m2'].sum() * (1 / square_m_per_square_km)

xx=1
