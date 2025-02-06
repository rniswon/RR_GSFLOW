#---- Settings ----------------------------------------------####

# load packages
import os, sys
import shutil
import numpy as np
import pandas as pd

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace

# set zonebudget zone file
zone_file = os.path.join(repo_ws, "GSFLOW", "scripts", "zone_budget", "zone_bud_subbasins.zon")



#---- Update zonebudget zone file ----------------------------------------------####

# read in zonebudget zone file
zones_text_r = open(zone_file, 'r')
lines = zones_text_r.readlines()
zones_text_r.close()
zones_text_w = open(zone_file, 'w')

# loop through content
num_spaces = 5
for line in lines:
    line = line.strip()

    # skip header lines
    if line == "3    411    253":
        zones_text_w.write(line)
        zones_text_w.write("\n")

    if line[0:8] == "INTERNAL":
        zones_text_w.write(line)
        zones_text_w.write("\n")

    # update values
    else:
        vals = line.strip().split()
        line_updated = []
        for val in vals:
            val = (num_spaces - len(val)) * ' ' + val
            line_updated.append(val)
        line_updated = "".join(line_updated)
        zones_text_w.write(line_updated)
        zones_text_w.write("\n")