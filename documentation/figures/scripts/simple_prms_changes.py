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
    fn = os.path.join(ws, basename + "sub_cfs.csv")
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
obs_streamflow_fn = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\scripts\inputs_for_scripts\RR_gage_and_other_flows.csv"
gage_hru_fn = r"D:\Workspace\projects\RussianRiver\Data\Archive_RR\rr_data_release\Observations\Observed Streamflow Gages\gage_info.shp"
gages_with_good_data = [1, 2, 3, 5, 6, 13, 18, 20]

# (2) Georeferencing
xoff = 465900.0
yoff = 4238400
epsg= 26910
ncol = 253
nrow = 411


# (3) load gsflow
control_file = os.path.join(ws, r"gsflow_rr.control")
gs = gsflow.GsflowModel.load_from_file(control_file=control_file, model_ws=ws, mf_load_only=['DIS', 'BAS6', 'UPW', 'sfr', 'UZF'])
mf = gs.mf



# (4) convert streamflow from depth to flow rate
# acre2meter = 4046.86
# inch2meter = 0.0254
ft2_to_acre = 1.0/43560.0
subbasin_id = gs.prms.parameters.get_values("hru_subbasin")
streamflow_sim = read_simulated_streamflow(gs)
for subbasin in streamflow_sim.columns:
    hru_area = gs.prms.parameters.get_values('hru_area')
    nhru = np.sum(subbasin_id>0)
    streamflow_sim[subbasin] = streamflow_sim[subbasin] * ft2_to_acre*60*60*24

# (5) read observed stream flow


gage_shp = geopandas.read_file(gage_hru_fn)
streamflow_obs = pd.read_csv(obs_streamflow_fn)
streamflow_obs['Date'] = pd.to_datetime(streamflow_obs['date'])
streamflow_obs.set_index('Date', inplace=True)
for igage, gage in gage_shp.iterrows():
    name = gage['Name']
    sub_id = gage['subbasin']
    if not(sub_id in gages_with_good_data):
        continue
    streamflow_obs[name] = streamflow_obs[name] * ft2_to_acre*60*60*24
    streamflow_obs.rename(columns={name:int(sub_id)}, inplace=True)
streamflow_obs = streamflow_obs[gages_with_good_data]

# (6) compare obs and sim
streamflow_obs['year'] = streamflow_obs.index.year
streamflow_sim['year'] = streamflow_sim.index.year

obs_annual = streamflow_obs.groupby(by = 'year').sum()
sim_annual = streamflow_sim.groupby(by = 'year').sum()
for i in gages_with_good_data:
    plt.figure()
    sim_annual[i].plot(label='sim')
    obs_annual[i].plot(label='obs')
    plt.title("Subbasin {}".format(i))
    plt.legend()

xx= 1



