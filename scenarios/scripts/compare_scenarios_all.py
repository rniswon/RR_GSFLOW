# ---- Import -------------------------------------------####

# import python packages
import os
import shutil


# import plotting scripts
import compare_budgets_watershed
import compare_budgets_subbasin
import compare_gaining_losing_streams
import compare_functional_flow_metrics_at_gauges
import compare_reservoirs
import compare_low_flow_relationships
import compare_climate_indices
import compare_streamflows
import compare_potter_valley_inflows




# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

# set model folders
# note: update as needed
historical_baseline_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline")
historical_unimpaired_folder = os.path.join(scenarios_ws, "models", "historical", "hist_unimpaired")
historical_frost_folder = os.path.join(scenarios_ws, "models", "historical", "hist_frost")
historical_baseline_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline_modsim")
historical_pv1_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv1_modsim")
historical_pv2_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv2_modsim")
CanESM2_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp45")
CanESM2_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp85")
CNRMCM5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CNRM-CM5_rcp45")
CNRMCM5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CNRM-CM5_rcp85")
HADGEM2ES_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2-ES_rcp45")
HADGEM2ES_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2-ES_rcp85")
MIROC5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp45")
MIROC5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp85")

# place model folders in list
# model_folders_list = [historical_baseline_folder,
#                       historical_unimpaired_folder,
#                       # historical_frost_folder,
#                       historical_baseline_modsim_folder,
#                       historical_pv1_modsim_folder,
#                       historical_pv2_modsim_folder,
#                       # CanESM2_rcp45_folder,
#                       # CanESM2_rcp85_folder,
#                       # CNRMCM5_rcp45_folder,
#                       # CNRMCM5_rcp85_folder,
#                       # HADGEM2ES_rcp45_folder,
#                       # HADGEM2ES_rcp85_folder,
#                       # MIROC5_rcp45_folder,
#                       # MIROC5_rcp85_folder
#                       ]
model_folders_list = [#historical_baseline_folder,
                      #historical_unimpaired_folder,
                      # historical_frost_folder,
                      historical_baseline_modsim_folder,
                      historical_pv1_modsim_folder,
                      historical_pv2_modsim_folder,
                      CanESM2_rcp45_folder,
                      CanESM2_rcp85_folder,
                      CNRMCM5_rcp45_folder,
                      CNRMCM5_rcp85_folder,
                      HADGEM2ES_rcp45_folder,
                      HADGEM2ES_rcp85_folder,
                      MIROC5_rcp45_folder,
                      MIROC5_rcp85_folder
                      ]

# set model names
# model_names = ['hist_baseline',
#                'hist_unimpaired',
#                # 'hist_frost',
#                'hist_baseline_modsim',
#                'hist_pv1_modsim',
#                'hist_pv2_modsim',
#                # 'CanESM2_rcp45',
#                # 'CanESM2_rcp85',
#                # 'CNRMCM5_rcp45',
#                # 'CNRMCM5_rcp85',
#                # 'HADGEM2ES_rcp45',
#                # 'HADGEM2ES_rcp85',
#                # 'MIROC5_rcp45',
#                # 'MIROC5_rcp85'
#                ]
model_names = [#'hist_baseline',
               #'hist_unimpaired',
               # 'hist_frost',
               'hist_baseline_modsim',
               'hist_pv1_modsim',
               'hist_pv2_modsim',
               'CanESM2_rcp45',
               'CanESM2_rcp85',
               'CNRM-CM5_rcp45',
               'CNRM-CM5_rcp85',
               'HADGEM2-ES_rcp45',
               'HADGEM2-ES_rcp85',
               'MIROC5_rcp45',
               'MIROC5_rcp85'
               ]

# set model names to be used for plot labels
# model_names_pretty = ['hist-baseline',
#                       'hist-unimpaired',
#                       # 'hist-frost',
#                       'hist-baseline-modsim',
#                       'hist-pv1-modsim',
#                       'hist-pv2-modsim',
#                       # 'CanESM2-rcp45',
#                       # 'CanESM2-rcp85',
#                       # 'CNRMCM5-rcp45',
#                       # 'CNRMCM5-rcp85',
#                       # 'HADGEM2ES-rcp45',
#                       # 'HADGEM2ES-rcp85',
#                       # 'MIROC5-rcp45',
#                       # 'MIROC5-rcp85'
#                       ]
model_names_pretty = [#'hist-baseline',
                      #'hist-unimpaired',
                      # 'hist-frost',
                      'hist-baseline-modsim',
                      'hist-pv1-modsim',
                      'hist-pv2-modsim',
                      'CanESM2-rcp45',
                      'CanESM2-rcp85',
                      'CNRM-CM5-rcp45',
                      'CNRM-CM5-rcp85',
                      'HADGEM2-ES-rcp45',
                      'HADGEM2-ES-rcp85',
                      'MIROC5-rcp45',
                      'MIROC5-rcp85'
                      ]

model_names_cc = [
    'CanESM2_rcp45',
    'CanESM2_rcp85',
    'CNRM-CM5_rcp45',
    'CNRM-CM5_rcp85',
    'HADGEM2-ES_rcp45',
    'HADGEM2-ES_rcp85',
    'MIROC5_rcp45',
    'MIROC5_rcp85'
]


model_names_hist_cc_rcp45 = [
    'hist_baseline_modsim',
    'hist_pv1_modsim',
    'hist_pv2_modsim',
    'CanESM2_rcp45',
    'CNRM-CM5_rcp45',
    'HADGEM2-ES_rcp45',
    'MIROC5_rcp45'
]


model_names_hist_cc_rcp85 = [
    'hist_baseline_modsim',
    'hist_pv1_modsim',
    'hist_pv2_modsim',
    'CanESM2_rcp85',
    'CNRM-CM5_rcp85',
    'HADGEM2-ES_rcp85',
    'MIROC5_rcp85'
]




# #---- Delete old plots and tables and regenerate -------------------------------------------####
#
# # delete and regenerate results workspace
# if not (os.path.isdir(results_ws)):
#     os.mkdir(results_ws)
# else:
#     shutil.rmtree(results_ws)
#     os.mkdir(results_ws)
#
# # delete and regenerate results workspace: plots
# plots_path = os.path.join(results_ws, "plots")
# if os.path.isdir(plots_path):
#     results_plot_folders = os.listdir(plots_path)
#     for plot_folder in results_plot_folders:
#         plot_path = os.path.join(results_ws, 'plots', plot_folder)
#         shutil.rmtree(plot_path)
#         os.mkdir(plot_path)
# else:
#     os.mkdir(os.path.join(results_ws, "plots"))
#     results_plot_folders = ['compare_budgets', 'compare_climate_indices', 'compare_functional_flow_metrics', 'compare_gaining_losing_streams', 'compare_low_flow_relationships', 'compare_reservoirs', 'compare_potter_valley_inflows']
#     for plot_folder in results_plot_folders:
#         plot_path = os.path.join(results_ws, 'plots', plot_folder)
#         os.mkdir(plot_path)
#
# # delete and regenerate results workspace: tables
# table_path = os.path.join(results_ws, 'tables')
# if os.path.isdir(table_path):
#     shutil.rmtree(table_path)
#     os.mkdir(table_path)
# else:
#     os.mkdir(table_path)





# ---- Run plotting scripts -------------------------------------------####

print('compare budgets: watershed')
compare_budgets_watershed.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)

# print('compare budgets: subbasin')
# compare_budgets_subbasin.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
#
# # # print('compare gaining and losing streams')
# # # compare_gaining_losing_streams.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty)

# print('compare functional flow metrics at gauges')
# compare_functional_flow_metrics_at_gauges.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)

# print('compare reservoirs')
# compare_reservoirs.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)

# # # print('compare low flow relationships')
# # # compare_low_flow_relationships.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
#
# print('compare climate indices')
# compare_climate_indices.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
#
# # print('compare streamflows')
# # compare_streamflows.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
#
# print('compare Potter Valley inflows')
# compare_potter_valley_inflows.main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)

