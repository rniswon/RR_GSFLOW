import os, sys
import numpy as np
import pandas as pd


class MParam(object):
    def __init__(self, filename = "case.tpl", par_names = [], delimiter = "#" ):
        self.filename = filename
        self.delimiter = delimiter
        self.par_names = par_names
        self.no_params = len(par_names)
        self.no_gparams = 1
        columns = ['par_gp_nme' , 'inc_typ', 'der_inc', 'der_inc_lb', 'for_cent', 'der_inc_mul',
                   'der_mthd','split_thresh', 'split_rel_diff', 'split_action']
        defualt_parm_gp = ['K', 'relative', 0.01, 0.0, 'switch', 2.0, 'parabolic', None, None, None]
        self._param_group_df = pd.DataFrame([defualt_parm_gp], columns=columns)

        columns = ['par_nme', 'par_trans', 'par_chg_lim', 'par_val1', 'par_lbnd', 'par_ubnd',
                   'par_gp', 'scale', 'offest', 'dercom']
        self._param_data_df = pd.DataFrame(columns=columns)

    @property
    def group_param(self):
        return self._param_group_df

    @group_param.setter
    def group_param(self,df):
        if isinstance(df, pd.DataFrame):
            self._param_group_df = df
        else:
            df_empty = self._param_group_df
            no_ = len(df)
            df_empty['par_gp_nme']= df
            df_empty['inc_typ'] = ['relative']*no_
            df_empty['der_inc'] = [0.01]*no_
            df_empty['der_inc_lb'] = [0.0] * no_
            df_empty['for_cent'] = ['switch'] * no_
            df_empty['der_inc_mul'] = [2.0] * no_

            df_empty['der_mthd'] = ['parabolic']* no_
            self.no_gparams = no_
            self._param_group_df = df_empty

    @property
    def param_data(self):
        return self._param_data_df

    @param_data.setter
    def param_data(self, df):
        if isinstance(df, pd.DataFrame):
            self._param_data_df = df
        else:
            df_empty = self._param_data_df
            no_ = len(df)
            df_empty['par_nme']= df
            df_empty['par_trans'] = ['log']*no_
            df_empty['par_chg_lim'] = ['factor']*no_
            df_empty['par_val1'] = [10.0] * no_
            df_empty['par_lbnd'] = [1e-10] * no_
            df_empty['par_ubnd'] = [1e10] * no_
            df_empty['scale'] = [1.0]* no_
            df_empty['offest'] = [0.0] * no_
            df_empty['dercom'] = [1] * no_
            df_empty['par_gp'] = ['K'] * no_
            self.no_params = no_
            self._param_data_df = df_empty

    def write_file(self):
        fid = open(self.filename,'w')
        fid.write("ptf %s\n"%(self.delimiter))
        par_names = self.param_data['par_nme'].values
        for nm in par_names:
            fid.write("%s %-15s %s\n"%(self.delimiter, nm, self.delimiter))

        fid.close()

class MObser(object):
    def __init__(self, filename="case.ins", obs_names=[], delimiter="$", obs_size = 25, obs_val=[]):
        self.filename = filename
        self.delimiter = delimiter
        self.obs_names = obs_names
        self.obs_size = obs_size
        self.obs_val = obs_val
        self.no_obs = 0
        columns = ['obs_g_name', 'Gt_arg', 'cov_file']
        default_go = ['head',None, None]
        self._obs_group_df = pd.DataFrame([default_go],columns=columns)
        columns = ['obs_name', 'obs_val', 'weight', 'obs_g_name']
        self._obs_df = pd.DataFrame(columns=columns)

    @property
    def group_obs(self):
        return self._obs_group_df

    @group_obs.setter
    def group_obs(self, df):
        if isinstance(df, pd.DataFrame):
            self._obs_group_df = df
        else:
            df_empty = self._param_group_df
            no_ = len(df)
            df_empty['obs_g_name'] = df
            self._obs_group_df = df_empty

    @property
    def obs_data(self):
        return self._obs_df

    @obs_data.setter
    def obs_data(self, df):
        if isinstance(df, pd.DataFrame):
            self._obs_df = df
        else:
            df_empty = self._obs_df
            no_ = len(df)
            df_empty['obs_name'] = df
            df_empty['weight'] = [1.0]*no_
            df_empty['obs_g_name'] = ['head']*no_

            self._obs_df = df_empty

    def write_ins_file(self):
        fid = open(self.filename, 'w')
        fid.write("pif %s\n" % (self.delimiter))
        obs_names = self.obs_data['obs_name'].values
        for nm in obs_names:
            fid.write("l1 ")
            fid.write("[{}]".format(nm))
            fid.write("1:{}".format(self.obs_size))
            fid.write("\n")


        fid.close()

if __name__ == "__main__":

    # conductivity 10
    para = []
    for i in np.arange(10):
        para.append("HK_%d"%(i))

    # storativity 10
    for i in np.arange(10):
        para.append("SS_%d"%(i))

    # faults permebility
    for i in np.arange(7):
        para.append("FHB_cond_%d"%(i))

    # param
    temp_par = MParam()
    temp_par.filename = "yuc.tpl"
    temp_par.param_data = para
    temp_par.write_file()

    #obs
    # heads
    obs=[]
    temp_obs = MObser()
    for i in np.arange(7):
        obs.append("HD%d" % (i))

    temp_obs.obs_data = obs
    temp_obs.write_ins_file()

    pass







