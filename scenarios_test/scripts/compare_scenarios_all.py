# ---- Import -------------------------------------------####

# import python packages
import os
import shutil


# import plotting scripts
import compare_budgets
import compare_gaining_losing_streams
import compare_functional_flow_metrics_at_gauges
import compare_reservoirs



# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace




#---- Delete old plots and tables and regenerate -------------------------------------------####

# delete and regenerate results workspace
if not (os.path.isdir(results_ws)):
    os.mkdir(results_ws)
else:
    shutil.rmtree(results_ws)
    os.mkdir(results_ws)

# delete and regenerate results workspace: plots
plots_path = os.path.join(results_ws, "plots")
if os.path.isdir(plots_path):
    results_plot_folders = os.listdir(plots_path)
    for plot_folder in results_plot_folders:
        plot_path = os.path.join(results_ws, 'plots', plot_folder)
        shutil.rmtree(plot_path)
        os.mkdir(plot_path)
else:
    os.mkdir(os.path.join(results_ws, "plots"))
    results_plot_folders = ['compare_budgets', 'compare_functional_flow_metrics', 'compare_gaining_losing_streams', 'compare_reservoirs']
    for plot_folder in results_plot_folders:
        plot_path = os.path.join(results_ws, 'plots', plot_folder)
        os.mkdir(plot_path)

# delete and regenerate results workspace: tables
table_path = os.path.join(results_ws, 'tables')
if os.path.isdir(table_path):
    shutil.rmtree(table_path)
    os.mkdir(table_path)
else:
    os.mkdir(table_path)





# ---- Run plotting scripts -------------------------------------------####

print('compare budgets')
compare_budgets.main(script_ws, scenarios_ws, results_ws)

print('compare gaining and losing streams')
compare_gaining_losing_streams.main(script_ws, scenarios_ws, results_ws)

print('compare functional flow metrics at gauges')
compare_functional_flow_metrics_at_gauges.main(script_ws, scenarios_ws, results_ws)

print('compare reservoirs')
compare_reservoirs.main(script_ws, scenarios_ws, results_ws)

