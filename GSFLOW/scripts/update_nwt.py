# Goal -------------------------------------------------------------------####

# Update NWT parameters using values from Ayman's NWT optimization


# Settings -------------------------------------------------------------------####

# import packages
import os, sys
import shutil
import numpy as np
import pandas as pd
import gsflow
import flopy

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221112_01")

# set file names
mf_name_file = os.path.join(model_ws, 'windows', 'rr_tr.nam')
search_grid_file = os.path.join(script_ws, 'inputs_for_scripts', 'search_grid.csv')
run_time_file = os.path.join(script_ws, 'inputs_for_scripts', 'run_time_results.csv')

# set number of fastest runs
num_fastest_runs = 10


# Read in -------------------------------------------------------------------####

# read in search grid file
search_grid = pd.read_csv(search_grid_file)

# read in run time file
run_time = pd.read_csv(run_time_file)

# load transient modflow model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                 load_only=["BAS6", "DIS", "NWT"],
                                 verbose=True, forgive=False, version="mfnwt")


# Identify fastest runs -------------------------------------------------------------------####

# sort
run_time = run_time.sort_values(by=['Time'])

# get run ids for n fastest runs
fastest_runs = run_time['id'][0:num_fastest_runs]


# Update NWT -------------------------------------------------------------------####

for run in fastest_runs:

    # get parameter values for this run
    df = search_grid[search_grid['id'] == run]

    # update nwt package values: dataset 1
    mf.nwt.headtol = df[df['pname'] == 'headtol']['pvalue'].values[0]
    mf.nwt.fluxtol = df[df['pname'] == 'fluxtol']['pvalue'].values[0]
    mf.nwt.maxiterout = int(df[df['pname'] == 'maxiterout']['pvalue'].values[0])
    mf.nwt.thickfact = df[df['pname'] == 'thickfact']['pvalue'].values[0]
    mf.nwt.linmeth = int(df[df['pname'] == 'linmeth']['pvalue'].values[0])
    mf.nwt.iprnwt = int(df[df['pname'] == 'iprnwt']['pvalue'].values[0])
    mf.nwt.ibotav = int(df[df['pname'] == 'ibotav']['pvalue'].values[0])
    mf.nwt.dbdtheta = df[df['pname'] == 'dbdtheta']['pvalue'].values[0]
    mf.nwt.dbdkappa = df[df['pname'] == 'dbdkappa']['pvalue'].values[0]
    mf.nwt.dbdgamma = df[df['pname'] == 'dbdgamma']['pvalue'].values[0]
    mf.nwt.momfact = df[df['pname'] == 'momfact']['pvalue'].values[0]
    mf.nwt.backflag = int(df[df['pname'] == 'backflag']['pvalue'].values[0])
    mf.nwt.maxbackiter = int(df[df['pname'] == 'maxbackiter']['pvalue'].values[0])
    mf.nwt.backtol = df[df['pname'] == 'backtol']['pvalue'].values[0]
    mf.nwt.backreduce = df[df['pname'] == 'backreduce']['pvalue'].values[0]

    # update nwt package values: dataset 2a
    mf.nwt.ilumethod = int(df[df['pname'] == 'ilumethod']['pvalue'].values[0])
    mf.nwt.levfill = int(df[df['pname'] == 'levfill']['pvalue'].values[0])
    mf.nwt.maxitinner = int(df[df['pname'] == 'maxitinner']['pvalue'].values[0])
    mf.nwt.msdr = int(df[df['pname'] == 'msdr']['pvalue'].values[0])
    mf.nwt.stoptol = df[df['pname'] == 'stoptol']['pvalue'].values[0]

    # update nwt package values: dataset 2b
    mf.nwt.iacl = int(df[df['pname'] == 'iacl']['pvalue'].values[0])
    mf.nwt.norder = int(df[df['pname'] == 'norder']['pvalue'].values[0])
    mf.nwt.level = int(df[df['pname'] == 'level']['pvalue'].values[0])
    mf.nwt.north = int(df[df['pname'] == 'north']['pvalue'].values[0])
    mf.nwt.iredsys = int(df[df['pname'] == 'iredsys']['pvalue'].values[0])
    mf.nwt.rrctols = df[df['pname'] == 'rrctols']['pvalue'].values[0]
    mf.nwt.idroptol = int(df[df['pname'] == 'idroptol']['pvalue'].values[0])
    mf.nwt.epsrn = df[df['pname'] == 'epsrn']['pvalue'].values[0]
    mf.nwt.hclosexmd = df[df['pname'] == 'hclosexmd']['pvalue'].values[0]
    mf.nwt.mxiterxmd = int(df[df['pname'] == 'mxiterxmd']['pvalue'].values[0])

    # write nwt file
    nwt_file_name = 'rr_tr_run' + str(int(run)) + '.nwt'
    mf.nwt.fn_path = os.path.join(model_ws, 'modflow', 'input', nwt_file_name)
    mf.nwt.write_file()