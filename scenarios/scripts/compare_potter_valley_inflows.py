import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
from datetime import date, datetime, timedelta
import geopandas
import gsflow
import flopy


def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc):

    # ---- Define functions -------------------------------------------####




    # ---- Loop through models and read in Potter Valley inflows, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    pv_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in potter valley inflow file
        pv_file_name = 'Potter_Valley_inflow.dat'
        pv_file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'input', pv_file_name)
        pv_out = pd.read_csv(pv_file_path, sep='\t', header=None)

        # reformat
        pv_df = pv_out.rename(columns={0: 'totim', 1: 'potter_valley_inflows', 2: 'date'})
        tmp = pv_df['date'].str.split(pat='#', expand=True)
        pv_df['date'] = tmp[[1]]
        pv_df['date'] = pd.to_datetime(pv_df['date'])
        pv_df['model'] = model_name_pretty

        # set values to 0 for hist-pv2-modsim
        if pv_df['model'].values[0] == 'hist-pv2-modsim':
            pv_df['potter_valley_inflows'] = 0

        # store in list
        pv_list.append(pv_df)

    # convert list to data frame
    pv_df_all = pd.concat(pv_list)

    # select models of interest
    pv_df_all = pv_df_all[pv_df_all['model'].isin(['hist-baseline-modsim', 'hist-pv1-modsim', 'hist-pv2-modsim'])]

    # select five years to focus on
    pv_df_all_select_years = pv_df_all[(pv_df_all['date'] > '2010-10-01') & (pv_df_all['date'] < '2015-09-30')]


    # ---- Plot -------------------------------------------####

    # plot
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))

    plot_title = 'a) Potter Valley Inflows: 1/1/1990-12/30/2015'
    p = sns.lineplot(data=pv_df_all, x="date", y="potter_valley_inflows", hue="model", style = 'model', legend=True, ax=axes[0])
    p.set_title(plot_title, loc='left')
    p.set_xlabel('Date')
    p.set_ylabel('Potter Valley inflows ($\mathregular{m^3}$/day)')
    p.legend(title='Model')

    plot_title = 'b) Potter Valley Inflows: 10/1/2010 - 9/30/2015'
    p = sns.lineplot(data=pv_df_all_select_years, x="date", y="potter_valley_inflows", hue="model", style = 'model', legend=True, ax=axes[1])
    p.set_title(plot_title, loc='left')
    p.set_xlabel('Date')
    p.set_ylabel('Potter Valley inflows ($\mathregular{m^3}$/day)')
    p.legend(title='Model')

    # export figure
    file_name = 'potter_valley_inflows.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_potter_valley_inflows', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')



if __name__ == "__main__":
    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
