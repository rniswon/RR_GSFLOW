This folder contains scripts used to generate plots and tables that compare scenarios.  


To compare the 11 scenarios that the paper focuses on (all except the historical baseline, historical unimpaired,
and historical frost protection) do the following:
1) Open up compare_scenarios_all.py
2) If you're trying to reproduce the figures/tables in the paper, don't make any changes to the commented/uncommented 
   portions of the script.  Only the parts of the script that are necessary for the paper figures are uncommented.
3) Run compare_scenarios_all.py
4) You'll find the results in this folder (file path relative to this script): ..\results


To compare the historical baseline, historical unimpaired, and historical frost protection models 
(these are only compared in the supplemental materials), run this script: 
compare_baseline_unimpaired_frost.py


To calculate the drought intensity, severity, and duration metrics, run this script: 
calculate_spei_time_chunks.R



