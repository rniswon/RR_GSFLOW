import os
import sys
import pandas as pd
import flopy
import gsflow


#---- Settings -------------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                          # script workspace
input_ws = os.path.join(script_ws, "inputs_for_scripts", "gsflow_climate_change_dis")           # input workspace
output_ws = os.path.join(script_ws, "script_outputs", "gsflow_climate_change_dis_updated")      # output workspace

# set dis file
dis_file = os.path.join(input_ws, "rr_climate.dis")

# set constants
model_name = 'rr_climate'
newlin = '\n'

# set modflow name file
mf_name_file = os.path.join(input_ws, "rr_CanESM2_rcp45_heavy.nam")



#---- Read in -------------------------------------------------------####

# read in modflow
# mc = flopy.modflow.Modflow(model_ws=thisFolder,
#                         modelname=model_name,
#                         version='mfnwt',
#                         start_datetime='1/1/1990')
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# read in dis
#dis = flopy.modflow.ModflowDis.load(dis_file, mf)
dis = mf.dis
nper = dis.nper
steps = dis.nstp
ntsp = steps.array


#---- Generate OC -------------------------------------------------------####

# oc: save head and budget for each str
print('building oc file...')
oc_file_path = os.path.join(output_ws, "rr_climate.oc")
oc_heavy_file_path = os.path.join(output_ws, "rr_climate_heavy.oc")

oc_out = open(oc_file_path, 'w')
oc_heavy_out = open(oc_heavy_file_path, 'w')
oc_out.write('# OC package for MODFLOW-NWT{}'.format(newlin))
oc_out.write('HEAD PRINT FORMAT       0{}'.format(newlin))
oc_out.write('HEAD SAVE UNIT         51{}'.format(newlin))
oc_out.write('DRAWDOWN PRINT FORMAT   0{}'.format(newlin))
oc_out.write('COMPACT BUDGET AUX{}'.format(newlin))
oc_heavy_out.write('# OC package for MODFLOW-NWT{}'.format(newlin))
oc_heavy_out.write('HEAD PRINT FORMAT       0{}'.format(newlin))
oc_heavy_out.write('HEAD SAVE UNIT         51{}'.format(newlin))
oc_heavy_out.write('DRAWDOWN PRINT FORMAT   0{}'.format(newlin))
oc_heavy_out.write('COMPACT BUDGET AUX{}'.format(newlin))
spd = {}
sphead = 0
headlist = []
# make a list of stress periods that are Feb or Sep (zero based)
for sp in range(nper):
    sphead += 1
    headlist.append(sphead)
    sphead += 7
    headlist.append(sphead)
    sphead += 4
for sp in range(nper):
    oc_out.write('period {} step {}{}'.format(sp + 1, ntsp[sp], newlin))
    oc_out.write('  print budget{}'.format(newlin))
    oc_out.write('  save budget{}'.format(newlin))
    oc_out.write('  save head{}'.format(newlin))
    if sp >= 309:    #  End of WY 2015
        for tsp in range(1, ntsp[sp]):
            oc_heavy_out.write('period {} step {}{}'.format(sp + 1, tsp, newlin))
            # oc_heavy_out.write('  print budget{}'.format(newlin))
            oc_heavy_out.write('  save budget{}'.format(newlin))
        oc_heavy_out.write('period {} step {}{}'.format(sp + 1, ntsp[sp], newlin))
        oc_heavy_out.write('  save budget{}'.format(newlin))
        if sp in headlist:
            oc_heavy_out.write('  save head{}'.format(newlin))
        oc_heavy_out.write('  print budget{}'.format(newlin))
    # spd[sp, ntsp[sp]] = ['save head', 'save budget', 'print budget']
# once again flopy doesn't work!
# oc = fp.modflow.ModflowOc(mc,
#                          stress_period_data=spd,
#                          filenames='./external_files/{}.oc'.format(model_name),
#                          compact=True)
# oc.write_file()
oc_out.close()
oc_heavy_out.close()
# distribute_file('{}.oc'.format(model_name), '{}.oc'.format(model_name))
# distribute_file('{}_heavy.oc'.format(model_name), '{}_heavy.oc'.format(model_name))