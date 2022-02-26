@echo off

:: Post-process GSFLOW model 
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_list_output.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe get_hobs_output.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_uzf_recharge_and_discharge.py
C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe plot_watershed_summary_time_series.py

pause