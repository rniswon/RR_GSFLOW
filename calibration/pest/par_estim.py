import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
class Control_data_section(object):
    def __init__(self,restart_flg = 'restart', mode = 'estimation', npar = 0, nobs = 0,
                 num_of_para_groups = 0, nprior = 0, num_of_obs_groups = 0, max_comp_dim = None,
                 der_zero_lim = None, num_input_files = 0, num_inst_files = 0, precision = "single",
                 dpoint = 'point', initial_lambda = 10.0, lambda_adj_factor=2.0, phi_ratio = 0.3,
                 increment_phi_ratio = 0.01, max_num_of_lambdas = 10, Broyden_Jacobian=0,
                 lambda_forgive = 'lamforgive', der_forgive = 'derforgive', max_rel_par_chg = 0.1,
                 max_fac_chg = None, max_abs_chg = None, fac_orig = 0.001, ibound_stick = 0,
                 up_vec_bend = 0, phi_reduc_switch = 0.1, no_prem_trip_switch = None, splt_slp_anal_swch = 0,
                 auto_user_interv =  'noaui', sen_reuse = "nosenreuse", bound_scale = "boundscale",
                 no_max_iter = 50, phi_red_stop = 0.005, no_phi_stop = 4, no_phi_no_red = 3,
                 rel_par_stop = 0.005, no_rel_par = 4, phi_stop_thresh = 0, last_run = 0, phi_abandon=10000,
                 icov = 1, icor = 1, ieig = 1, ires = 1, joc_save = "jcosave", joc_save_iter = "nojcosaveitn",
                 verbose_rec = "noverboserec", rei_save_iter = "reisaveitn", par_save_iter = "parsaveitn",
                 par_save_run = "parsaverun"):


        self.restart_flg = restart_flg
        self.mode = mode
        self.restart_flg_options = ['restart', 'norestart']
        self.npar = npar
        self.nobs = nobs
        self.num_of_para_groups = num_of_para_groups
        self.nprior = nprior
        self.num_of_obs_groups = num_of_obs_groups
        self.max_comp_dim = max_comp_dim
        self.der_zero_lim = der_zero_lim
        self.num_input_files = num_input_files
        self.num_inst_files = num_inst_files
        self.precision = precision
        self.dpoint = dpoint
        self.num_com_jacfile_messFile = [1, 0 , 0]
        self.obs_re_ref = 'noobsreref'
        # fifth line
        self.initial_lambda = initial_lambda
        self.lambda_adj_factor = lambda_adj_factor
        self.phi_ratio = phi_ratio
        self.increment_phi_ratio = increment_phi_ratio
        self.max_num_of_lambdas= max_num_of_lambdas
        self.Broyden_Jacobian = Broyden_Jacobian
        self.lambda_forgive = lambda_forgive
        self.der_forgive = der_forgive


        # sixth line
        self.max_rel_par_chg = max_rel_par_chg
        self.max_fac_chg = max_fac_chg
        self.max_abs_chg = max_abs_chg
        self.fac_orig = fac_orig
        self.ibound_stick = ibound_stick
        self.up_vec_bend = up_vec_bend

        # 7th line
        self.phi_reduc_switch = phi_reduc_switch
        self.no_prem_trip_switch = no_prem_trip_switch
        self.splt_slp_anal_swch = splt_slp_anal_swch
        self.auto_user_interv = auto_user_interv
        self.sen_reuse = sen_reuse
        self.bound_scale = bound_scale

        #8th line
        self.no_max_iter = no_max_iter
        self.phi_red_stop = phi_red_stop
        self.no_phi_stop = no_phi_stop
        self.no_phi_no_red = no_phi_no_red
        self.rel_par_stop = rel_par_stop
        self.no_rel_par = no_rel_par
        self.phi_stop_thresh = phi_stop_thresh
        self.last_run = last_run
        self.phi_abandon = phi_abandon

        #9th line
        self.icov = icov
        self.icor = icor
        self.ieig = ieig
        self.ires = ires
        self.joc_save = joc_save
        self.joc_save_iter = joc_save_iter
        self.verbose_rec = verbose_rec
        self.rei_save_iter = rei_save_iter
        self.par_save_iter = par_save_iter
        self.par_save_run = par_save_run

    def write(self,fid):

        # L1
        fid.write("* control data\n")
        #L2
        fid.write("%s %s\n".format(self.restart_flg,self.mode))
        # L3
        fid.write("%d %d %d %d".format(self.npar, self.nobs, self.num_of_para_groups, self.nprior
                                       , self.num_of_obs_groups))
        if not self.max_comp_dim == None:
            fid.write(" %d".format(self.max_comp_dim))
        if not self.der_zero_lim == None:
            fid.write(" %d\n".format(self.der_zero_lim))
        # L4
        fid.write("%d %d %s %s %d %d %d %s\n".format(self.num_input_files, self.num_inst_files,
                                    self.precision, self.dpoint, self.num_com_jacfile_messFile[0],
                                                self.num_com_jacfile_messFile[1], self.num_com_jacfile_messFile[2]
                                                ,  self.obs_re_ref))
        #L5
        fid.write("%f %f %f %f %d %d %s %s\n".format(self.initial_lambda, self.lambda_adj_factor,
                                                   self.phi_ratio, self.increment_phi_ratio,
                                                   self.max_num_of_lambdas,self.Broyden_Jacobian,
                                                   self.lambda_forgive,self.der_forgive ))
        #L6
        if not self.max_rel_par_chg == None:
            fid.write("%f ".format(self.max_rel_par_chg))
        if not self.max_fac_chg == None:
            fid.write("%f ".format(self.max_fac_chg))
        if not self.max_abs_chg == None:
            fid.write("%f ".format(self.max_abs_chg))
        if not self.ibound_stick == None:
            fid.write("%f ".format(self.ibound_stick))
        if not self.up_vec_bend == None:
            fid.write("%f ".format(self.up_vec_bend))
        fid.write("\n")

        #L7
        if not self.phi_reduc_switch == None:
            fid.write("%f ".format(self.phi_reduc_switch))
        if not self.no_prem_trip_switch == None:
            fid.write("%f ".format(self.no_prem_trip_switch))
        if not self.no_prem_trip_switch == None:
            fid.write("%f ".format(self.no_prem_trip_switch))
        if not self.splt_slp_anal_swch == None:
            fid.write("%f ".format(self.splt_slp_anal_swch))
        if not self.splt_slp_anal_swch == None:
            fid.write("%f ".format(self.splt_slp_anal_swch))
        if not self.auto_user_interv == None:
            fid.write("%s ".format(self.auto_user_interv))
        if not self.sen_reuse == None:
            fid.write("%s ".format(self.sen_reuse))
        if not self.bound_scale == None:
            fid.write("%s ".format(self.bound_scale))
        fid.write("\n")

        #L8
        fid.write("%d ".format(self.no_max_iter))
        fid.write("%f ".format(self.phi_red_stop))
        fid.write("%d ".format(self.no_phi_stop))
        fid.write("%d ".format(self.no_phi_no_red))
        fid.write("%f ".format(self.rel_par_stop))
        fid.write("%d ".format(self.no_rel_par))
        fid.write("%f ".format(self.phi_stop_thresh))
        fid.write("%f ".format(self.last_run))
        fid.write("%f ".format(self.phi_abandon))
        fid.write("\n")

        #L9
        fid.write("%d ".format(self.icov))
        fid.write("%d ".format(self.icor))
        fid.write("%d ".format(self.ieig))
        fid.write("%d ".format(self.ires))
        fid.write("%s ".format(self.joc_save))
        fid.write("%s ".format(self.joc_save_iter))
        fid.write("%s ".format(self.verbose_rec))
        fid.write("%s ".format(self.rei_save_iter))
        fid.write("%s ".format(self.par_save_iter))
        fid.write("%s ".format(self.par_save_run))
        fid.write("\n")

class Control(object):
    def __init__(self, fname = 'proj.pst',  ):
        self.file_name = fname
        self.control_data = Control_data_section()
        pass

    def write_file(self):
        fn = self.file_name
        fid = open(fn, 'w')
        fid.write("pcf\n")
        fid.control_data.write()


        pass


class Calibration(object):
    def __init__(self):
        self.control = Control
        self.mode = "estimation"
        self.mode_options = ['predictive analysis', 'regularisation', 'pareto', 'estimation' ]

        pass



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
    par = np.array([1.5, 5, 2.33])
    yy = model(par)

    # measurments
    indx = [5, 95, 125, 130, 193]
    error = 50 * np.array([-1.61396718, -1.34331275, 0.2489252, 0.79696246, 0.07488841])
    yo = yy[indx] + error
    plt.plot(xx, yy)
    plt.scatter(xx[indx], yo)

    con_dat = Control_data_section()
    pass