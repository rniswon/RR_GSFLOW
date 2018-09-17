import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Nonlinear_Param_Estimator(object):
    def __init__(self, func, xi, yo):
        self.xi = xi # initial parameters
        self.xc = xi
        self.func = func
        self.yo = yo # observations
        self.n = len(self.xi) # number of parameters
        self.m = len(self.yo) # number of observations
        self.convg_flg = 0

    def func_evalute(self, x):
        # evalute the function using the current parameter xc
        print "Evalute the function ...."
        y = self.func(x)
        print "Finish function evaluation...."
        return y

    def residual(self,x):
        y = self.func_evalute(x)
        err = np.power((y-self.yo),2.0)
        return np.sum(err)


    def compute_jacobian(self):

        J = np.zeros_like(m,n,dtype=float)

        for par_id in range(n):
            xp = np.copy(self.xc)
            xp[par_id]  = xp[par_id] * 1.01
            yp = self.func_evalute(self, xp)
            jac = (yp - self.yc)/(xp[par_id]-self.xc[par_id])
            J[:,par_id] = jac
        self.J = J

    def estimate(self):
        self.compute_jacobian()
        JtJ = self.J.transpose()* self.J
        B = np.eye(self.n,self.n)
        self.xnew = 1




    # def calibrate(self):
    #     while not self.convg_flg:
    #        self.estimate()
    #         self.x
    #     else:
    #         print "Converged...."
    #







if __name__ == "__main__":

    def model(x):
        a = x[0]
        b = x[1]
        c = x[2]
        xx = np.arange(-10,10,0.1)
        yy = a + b*np.power(xx,3.5) - c*np.power(xx,2.1)
        return yy


    xx = np.arange(-10, 10, 0.1)

    # true parameters
    par = np.array([1.5,5,2.33])
    yy = model(par)

    # measurments
    indx = [5, 95, 125,130, 193 ]
    error = 50 * np.array([-1.61396718, -1.34331275, 0.2489252, 0.79696246, 0.07488841])
    yo = yy[indx] + error
    plt.plot(xx,yy)
    plt.scatter(xx[indx],yo)

    # setup calib example
    cal_ex = Nonlinear_Param_Estimator(func = model, xi=[1,1,1], yo=yo)




    pass




