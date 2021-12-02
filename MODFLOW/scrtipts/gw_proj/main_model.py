import os, sys

Use_Develop_FLOPY = False   # NOTE: Ayman had this set to True, I don't currently have the develop version of flopy so keep it as False

if Use_Develop_FLOPY:
    fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")   # TODO: change this file path once get develop version of flopy and store it locally
    sys.path.append(fpth)
    import flopy
else:
    import flopy

import numpy as np
import pandas as pd
import configparser
# import flopy
# package for RR project
from gw import Gw_model
# from includes import Include
import support
import Compute_Lake2
config_file = r"rr_ss_config.ini"
config = configparser.ConfigParser()
config.read(config_file)

# initialize GW model
gw = Gw_model(config)

# generating dis package
gw.dis_package()

# generate bas package
fn = r"..\..\other_files\rr_ss_v4.hds"
hds1 = flopy.utils.HeadFile(fn)
wt = hds1.get_data(kstpkper = (0,0))
wt[wt>2000] = 235
#wt = None
gw.bas_package(wt)
#gw.bas_package_01(wt)

# generate ghb package
gw.ghb_package()

# modify the grid to carve lakes
Compute_Lake2.carve_lakes(gw)

# generate boundary conditions


# generate upw package
geo_zones = []
gw.upw_package(geo_zones)

# generate hfb
gw.hfb_package()

# generate sfr2 package
#gw.sfr2_package()

# generate sfr3 package
gw.sfr3_package()

# generate uzf package
gw.uzf_package()

# generate lak package
gw.lak_package()
#gw.mf.lak.write_file()

# generate gage package


# generate well package
#gw.well_package()
gw.well_package2()

# generate hob package
gw.hob_package()

# generate gage package
gw.gage_package() #TODO: unit number assignment for steady state model might be incorrect here

# generate Control package
gw.oc_package()

# for steady-state
if False:
    gw.rch_package()

# generate hfb


# generate obs

# generate nwt
nwt = flopy.modflow.mfnwt.ModflowNwt.load(r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\other_files\solver_options4.nwt",
                                     gw.mf)
nwt = flopy.modflow.mfnwt.ModflowNwt.load(r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\other_files\solver_options4.nwt",
                                     gw.mfs)


# Possible Unit bug
gw.mf.external_output = [False] * len(gw.mf.external_fnames)
gw.mfs.external_output = [False] * len(gw.mfs.external_fnames)

# generate transient model
gw.mf.write_input()

# generate steady state model
gw.mfs.write_input()
xx = 1




