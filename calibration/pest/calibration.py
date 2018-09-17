import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from control import Control


class Calibration(object):
    def __init__(self):
        self.control = Control()
        self.pest_exe= os.path.join(os.getcwd(),r".\pest14\pest.exe")
        self.model_python_fn = 'model.py'



    def generate_model_batch_file(self, fn):
        cmd = 'python.exe'
        cmd = cmd + " " + self.model_python_fn
        fid = open(fn,'w')
        fid.write(cmd)
        fid.close()
        self.control.COMLINE = fn


if __name__ == "__main__":
    def model(x):
        a = x[0]
        b = x[1]
        c = x[2]
        xx = np.arange(10, 30, 0.1)
        yy = (a + b*np.power(xx,3.5) - c*np.power(xx,2.1))
        return yy

    xx = np.arange(10, 30, 0.1)

    # true parameters
    par = np.array([0, 5, 2.33])
    yy = model(par)

    # measurments
    indx = [50, 95, 125, 130, 193]
    error = 0.1 * np.array([-1.61396718, -1.34331275, 0.2489252, 0.79696246, 0.07488841])
    yo = yy[indx] + error
    plt.plot(xx, yy)
    plt.scatter(xx[indx], yo, color='red')

    # Prepare Pest input file
    para = ['a', 'b', 'c']
    cal_proj = Calibration()
    cal_proj.control.MParam.filename = 'Test.tpl'
    cal_proj.control.MParam.param_data = para
    cal_proj.control.MParam.write_file()

    # obs
    # heads
    obs = []
    for i in np.arange(len(yo)):
        obs.append("obs1%d" % (i))

    cal_proj.control.MObser.obs_data = obs
    cal_proj.control.MObser.filename = 'test.ins'
    cal_proj.control.MObser.obs_data['obs_val'] = yo
    cal_proj.control.MObser.write_ins_file()
    cal_proj.control.filename = "test.pst"
    cal_proj.control.INFLE = 'input.dat'
    cal_proj.control.OUTFLE = 'output.dat'
    cal_proj.generate_model_batch_file('runmodel.bat')
    cal_proj.control.write()





    pass

