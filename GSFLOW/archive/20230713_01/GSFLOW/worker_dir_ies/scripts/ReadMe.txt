These are python scripts used for running the forward model and for plotting the calibrated model.

For plotting most aspects of the calibrated model, do the following:
1) Open the plot_all_gsflow.py script.  
2) If you're trying to re-generate the plots from the Russian River paper, 
   don't change the commented/uncommented portions of the script.  Portions 
   of the scripts that are not necessary for regenerating the plots and tables 
   in the paper are already commented out.
3) Run plot_all_gsflow.py
4) You will find the results in the following folder (relative to this file): ..\results


To calculate irrigated area, run:
calculate_irrigated_area.py


To generate parameter tables, run:
generate_param_tables.py


To calculate agricultural water use, run:
calculate_ag_water_use.py

