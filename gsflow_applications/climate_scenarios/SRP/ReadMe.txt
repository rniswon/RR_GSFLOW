Folder for climate scenarios

Data for climate scenarios was downloaded from Cal-Adapt: https://cal-adapt.org/data/download/
Models include both RCP45 and 85 scenarios
	CanESM2
	CNRM-CM5
	HadGEM2-ES
	MIROC5
	
Data units		GCM			SRPHM	Russian River
	Temperature: 	Kelvin (-273.15 C)	deg F		deg C
	PPT		kg/m2/s (mm/s)		in/d		mm/d

The various csv files downloaded were processed and converted into correct units,
and saved in a single csv file for the historical period and another for the future
period.

There are two weather stations that the SRPHM uses in the PRMS data file, one near 
Santa Rosa, and the other near the airport. Data for both locations were downloaded
and stored in two folders
	o scripts for bias correcting climate data, extracting budget data, and generating plots
		+ build_gcm_table.py: The climate data used in the SRPHM are read from 
		  Climate_stresses_update_1947_2018.dat and used as the observed historical data 
		  for both stations. It then reads downloaded time series data sets for both stations  
		  and all models and scenarios, and historical and future data. The data are converted 
		  to deg F and inches per day, and saved in gcm_historical_srphm.csv, and 
		  gcm_future_srphm.csv with a column for date and columns for each model and
		  scenario. 
		+ build_data_file.py: reads the original data file and appends corrected GCM data
		  to the end. This creates a new data file for each model and scenario, 8 in all.
		  file names are <model>_<scenario>_srphm_corrected_future.data
		+ bias_correct.py: The future data are read from gcm_srphm_future.csv and the 
		  historical data read from gcm_historicalsrphm.csv and the future data bias 
		  corrected using the histrical observed and model data, and saved in 
		  gcm_srphm_future_corrected.csv.
		+ plot_gcm_ppt_temp_dev.py: plots comparisons between the original and corrected
		  data. Plots are saved in the climate_scenarios/plots/ folder.
