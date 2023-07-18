Version:
This is version 20230603_01 of the GSFLOW model for the Russian River watershed.

Instructions for running GSFLOW:
- To run the model and generate daily budgets use rr_gsflow_model_shared\gsflow_model\windows\run_heavy.bat.
  This will produce about 100 GB of output.
- If you don't need the daily budgets, then use rr_gsflow_model_shared\gsflow_model\windows\run.bat.
  This will produce about 7 GB of output.
  
Instructions for running the zone budget utility:
- Note that the zone budget results are only meaningful if you've generated daily budgets 
  (i.e. if you've used rr_gsflow_model_shared\gsflow_model\windows\run_heavy.bat to run the model)
- To run zonebudget for the entire watershed, use: 
  rr_gsflow_model_shared\scripts\zone_budget\zone_budget_watershed.bat
- To run zonebudget for each subbasin, use: 
  rr_gsflow_model_shared\scripts\zone_budget\zone_budget_subbasin.bat
- The results will show up at the file path in the first line of:
		- rr_gsflow_model_shared\scripts\zone_budget\zb_cmd_watershed.txt (if running a budget for the entire watershed)
		- rr_gsflow_model_shared\scripts\zone_budget\zb_cmd_subbasins.txt (if running subbasin budgets) 