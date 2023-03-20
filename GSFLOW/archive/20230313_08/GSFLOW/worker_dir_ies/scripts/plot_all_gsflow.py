# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import matplotlib.pyplot as plt
import matplotlib
import importlib



# import plotting scripts
import plot_ag_diversions
import plot_ag_diversions_iupseg
import plot_ag_pond_div_iupseg
import plot_ag_pond_diversions
import plot_ag_pond_water_demand_and_use
import plot_ag_water_budget_by_subbasin_prms_only
import plot_ag_water_use
import plot_rainfall_runoff_ratio
import plot_gage_output
import plot_gsflow_inputs
import plot_hobs_output
import plot_infiltration
import plot_initial_tr_heads
import plot_lake_bathymetry
import plot_lake_outputs
import plot_list_output
import plot_pumping_reduction
import plot_pumping_reduction_mnw
import plot_sim_tr_heads
import plot_uzf_recharge_and_discharge
import plot_water_budget_by_subbasin
import plot_water_budget_by_subbasin_light
import plot_water_budget_by_subbasin_prms_only
import plot_watershed_summary_time_series



# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                  # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                        # model workspace
results_ws = os.path.join(model_ws, "..", "results")                                          # results workspace
#ss_archived_models_ws = os.path.join(repo_ws, "MODFLOW", "archived_models")            # steady state archived models workspace
#init_files_ws = os.path.join(repo_ws, "MODFLOW", "init_files")                         # modflow init files workspace

# set name file
mf_name_file_type = 'rr_tr.nam'  # options: rr_tr.nam or rr_tr_heavy.nam


#---- Delete old plots and tables -------------------------------------------####

# delete and regenerate contents of results workspace: plots
if not (os.path.isdir(results_ws)):
    os.mkdir(results_ws)
else:
    shutil.rmtree(results_ws)
    os.mkdir(results_ws)

if os.path.isdir(os.path.join(results_ws, "plots")):
    results_plot_folders = os.listdir(os.path.join(results_ws, "plots"))
else:
    os.mkdir(os.path.join(results_ws, "plots"))
    os.mkdir(os.path.join(results_ws, "tables"))


if 0:
    for plot_folder in results_plot_folders:
        plot_path = os.path.join(results_ws, 'plots', plot_folder)
        shutil.rmtree(plot_path)
        os.mkdir(plot_path)


if 0:
    # delete and regenerate contents of results workspace: tables
    table_path = os.path.join(results_ws, 'tables')
    shutil.rmtree(table_path)
    os.mkdir(table_path)




# ---- Run plotting scripts -------------------------------------------####

# print('plot ag diversions')
# plot_ag_diversions.main(model_ws, results_ws, mf_name_file_type)
#
# print('plot ag diversions iupseg')
# plot_ag_diversions_iupseg.main(model_ws, results_ws, mf_name_file_type)
#
# print('plot ag pond diversions iupseg')
# plot_ag_pond_div_iupseg.main(model_ws, results_ws, mf_name_file_type)
#
# print('plot ag pond diversions')
# plot_ag_pond_diversions.main(model_ws, results_ws, mf_name_file_type)
#
# print('plot ag pond water demand and use')
# plot_ag_pond_water_demand_and_use.main(script_ws, model_ws, results_ws, mf_name_file_type)
#
# # print('plot ag water budget by subbasin: prms only')
# # plot_ag_water_budget_by_subbasin_prms_only.main(model_ws, results_ws, mf_name_file_type)
#
# print('plot ag water use')
# plot_ag_water_use.main(model_ws, results_ws, mf_name_file_type)

# print('plot annual rainfall-runoff ratio')
# plot_rainfall_runoff_ratio.main(script_ws, model_ws, results_ws, mf_name_file_type)

print('plot gage output')
plot_gage_output.main(script_ws, model_ws, results_ws, mf_name_file_type)

# print('plot gsflow inputs')
# plot_gsflow_inputs.main(model_ws, results_ws, mf_name_file_type)

print('plot hobs output')
plot_hobs_output.main(script_ws, model_ws, results_ws, mf_name_file_type)

# print('plot infiltration')
# plot_infiltration.main(model_ws, results_ws, mf_name_file_type)

# print('plot initial transient heads') #todo: Ayman: no plots are made here
# plot_initial_tr_heads.main(model_ws, results_ws, ss_archived_models_ws, mf_name_file_type)

# print('plot lake bathymetry')
# plot_lake_bathymetry.main(script_ws, model_ws, results_ws, mf_name_file_type)

print('plot lake outputs')
plot_lake_outputs.main(script_ws, model_ws, results_ws, mf_name_file_type)

print('plot list output')
plot_list_output.main(model_ws, results_ws, mf_name_file_type)

print('plot pumping reduction')
#plot_pumping_reduction.main(script_ws, model_ws, results_ws, mf_name_file_type)
plot_pumping_reduction_mnw.main(script_ws, model_ws, results_ws, mf_name_file_type)

# print('plot simulated transient heads')
# plot_sim_tr_heads.main(model_ws, results_ws, mf_name_file_type)

# print('plot uzf recharge and discharge')
# plot_uzf_recharge_and_discharge.main(model_ws, results_ws, mf_name_file_type)

# print('plot water budget by subbasin')
# plot_water_budget_by_subbasin.main(script_ws, model_ws, results_ws, mf_name_file_type)

# print('plot water budget by subbasin light')
# plot_water_budget_by_subbasin_light.main(script_ws, model_ws, results_ws, mf_name_file_type)

# print('plot water budget by subbasin: prms only')
# plot_water_budget_by_subbasin_prms_only.main(script_ws, model_ws, results_ws, mf_name_file_type)

print('plot watershed summary time series')
plot_watershed_summary_time_series.main(model_ws, results_ws, mf_name_file_type)




# ---- Copy results folder into model workspace -------------------------------------------####

#shutil.copy(results_ws, model_ws)

#end = 1