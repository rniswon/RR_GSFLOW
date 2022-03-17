import os, sys
import flopy
import matplotlib.pyplot as plt


hds_file = r"C:\Users\aalzraiee\Downloads\rrsave_ss.hds"
hds = flopy.utils.HeadFile(hds_file)

xx = 1