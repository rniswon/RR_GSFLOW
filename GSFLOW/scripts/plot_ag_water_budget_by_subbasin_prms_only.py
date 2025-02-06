import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util


def main(model_ws, results_ws, mf_name_file_type):

    # ---- Settings ---------------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")
    # model_ws = os.path.join(repo_ws, "GSFLOW")

    # set gsflow and prms control files
    gsflow_control_file = os.path.join(model_ws, "windows", "gsflow_rr.control")
    prms_control = os.path.join(model_ws, 'windows', 'prms_rr.control')

    # set precip file
    precip_file = os.path.join(model_ws, "PRMS", "output", "nhru_hru_ppt_yearly.csv")

    # set potential ET file
    potet_file = os.path.join(model_ws, "PRMS", "output", "nhru_potet_yearly.csv")

    # set actual ET file
    actet_file = os.path.join(model_ws, "PRMS", "output", "nhru_hru_actet_yearly.csv")

    # set recharge file
    recharge_file = os.path.join(model_ws, "PRMS", "output", "nhru_recharge_yearly.csv")

    # set surface runoff file
    sroff_file = os.path.join(model_ws, "PRMS", "output", "nhru_sroff_yearly.csv")

    # set subsurface reservoir flow file
    ssres_flow_file = os.path.join(model_ws, "PRMS", "output", "nhru_ssres_flow_yearly.csv")

    # set subbasin area table
    subbasin_areas_file = os.path.join(model_ws, "scripts", "inputs_for_scripts", "subbasin_areas.txt")

    # # set file name for daily budget table
    # budget_subbasin_daily_file = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'ag_budget_subbasin_daily.csv')

    # # set file name for monthly budget table
    # budget_subbasin_monthly_file = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'ag_budget_subbasin_monthly.csv')

    # set file name for annual budget table
    budget_subbasin_annual_file = os.path.join(results_ws, 'tables', 'ag_budget_subbasin_annual.csv')

    # set plot folder name
    plot_folder = os.path.join(results_ws, 'plots', 'water_budget_ag')

    # set conversion factors
    inches_per_meter = 39.3700787

    # set start and end dates for simulation
    start_date = "1990-01-01"
    end_date = "2015-12-31"


    #---- Function to read in PRMS outputs and reformat ---------------------------------------------------------####

    def read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac):

        # # read in subbasin areas (needed to convert units of PRMS outputs)
        # subbasin_areas = pd.read_csv(subbasin_areas_file)
        # subbasin_areas['subbasin'] = subbasin_areas['subbasin'].astype(int)
        # subs = subbasin_areas['subbasin'].values

        # read in prms output file
        prms_output = pd.read_csv(prms_output_file)

        # reformat
        prms_output = pd.melt(prms_output, id_vars = ['Date'], var_name = 'hru_id', value_name = prms_var_name)
        prms_output['hru_id'] = prms_output['hru_id'].astype(np.int64)
        prms_output = pd.pivot(prms_output, index='hru_id', columns='Date', values=prms_var_name).reset_index()
        prms_output['subbasin'] = hru_subbasin
        prms_output['ag_frac']  = ag_frac
        prms_output['variable'] = prms_var_name
        prms_output = pd.melt(prms_output, id_vars = ['variable', 'subbasin', 'hru_id', 'ag_frac'], var_name = 'year', value_name = 'value')  # TODO: export this version  of the table for later use?

        # remove non-ag, group by subbasin, get mean over ag fields per subbasin
        mask = (prms_output['ag_frac'] > 0) & (prms_output['subbasin'] > 0)
        prms_output = prms_output.loc[mask]
        mean_ag_by_subbasin = prms_output.groupby(['variable', 'subbasin', 'year'])['value'].mean().reset_index()

        return mean_ag_by_subbasin




    #---- Get prms param ---------------------------------------------------------####

    # read in gsflow
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

    # get hru_subbasin
    hru_subbasin = gs.prms.parameters.get_values('hru_subbasin')

    # get ag_frac
    ag_frac = gs.prms.parameters.get_values('ag_frac')



    #---- Read in PRMS outputs ---------------------------------------------------------####

    # precip
    prms_output_file = precip_file
    prms_var_name = 'precip'
    precip_mean_ag = read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)

    # potet
    prms_output_file = potet_file
    prms_var_name = 'potet'
    potet_mean_ag = read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)

    # actet
    prms_output_file = actet_file
    prms_var_name = 'actet'
    actet_mean_ag =read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)

    # recharge
    prms_output_file = recharge_file
    prms_var_name = 'recharge'
    recharge_mean_ag =read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)

    # sroff
    prms_output_file = sroff_file
    prms_var_name = 'sroff'
    sroff_mean_ag = read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)

    # ssres_flow
    prms_output_file = ssres_flow_file
    prms_var_name = 'ssres_flow'
    ssres_flow_mean_ag = read_prms_output_and_reformat(prms_output_file, prms_var_name, subbasin_areas_file, hru_subbasin, ag_frac)



    #---- Reformat all into one table ---------------------------------------------------------####

    dfs = [precip_mean_ag, potet_mean_ag, actet_mean_ag, recharge_mean_ag, sroff_mean_ag, ssres_flow_mean_ag]
    budget_annual = pd.concat(dfs).reset_index()



    #---- Export csv of annual sums of budget components ---------------------------------------------------------####



    #---- Plot annual sums of budget components ---------------------------------------------------------####

    # loop through subbasins
    subs = budget_annual['subbasin'].unique()
    for sub in subs:

        # subset
        df_all = budget_annual[budget_annual['subbasin'] == sub]

        # # convert to long form
        # df_all = df_all.drop('subbasin', 1)
        # df_all = pd.melt(df_all,  id_vars=['year'], var_name='variable', value_name='value')

        # plot surface water budget
        selected_vars = ['precip', 'potet', 'actet', 'recharge', 'sroff', 'ssres_flow']
        df = df_all[df_all['variable'].isin(selected_vars)]
        plt.figure(figsize=(12, 8))
        sns.set(style='white')
        this_plot = sns.lineplot(x='year',
                                 y='value',
                                 hue='variable',
                                 style='variable',
                                 data=df)
        this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'surface water budget for field HRUs, annual sum, spatial mean')
        this_plot.set_xlabel('Year')
        this_plot.set_ylabel('Depth (in)')
        file_name = 'surface_water_budget_ag_' + str(sub) + '.png'
        file_path = os.path.join(plot_folder, file_name)
        fig = this_plot.get_figure()
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        fig.savefig(file_path)
        plt.close('all')


if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)