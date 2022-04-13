@echo off

:: Post-process GSFLOW model 
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_gsflow_inputs.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_list_output.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_watershed_summary_time_series.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_sim_tr_heads.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_uzf_recharge_and_discharge.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_pumping_reduction.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_infiltration.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_hobs_output.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_gage_output.py

pause