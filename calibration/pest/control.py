import os,sys
import numpy as np
import pandas as pd
from par_templ import MParam, MObser

class Control(MParam, MObser):
    def __init__(self, filename = 'case.pst', MParam = MParam,  MObser = MObser ):
        self.filename = filename
        self.sections = []
        self.__read_template()
        self.MParam = MParam()
        self.MObser = MObser()
        self.param_group_keys = {'PARGPNME': 'par_gp_nme',
                                 'INCTYP': 'par_gp_nme', 'DERINC': 'der_inc',
                                 'DERINCLB': 'der_inc_lb', 'FORCEN': 'for_cent',
                                 'DERINCMUL': 'der_inc_mul', 'DERMTHD': 'der_mthd',
                                 'SPLITTHRESH': 'split_thresh', 'SPLITRELDIFF': 'split_rel_diff',
                                 'SPLITACTION': 'split_action'}


        self.param_data_keys = {'PARNME':'par_nme', 'PARTRANS':'par_trans','PARCHGLIM':'par_chg_lim'
                                ,'PARVAL1':'par_val1', 'PARLBND': 'par_lbnd',
                                'PARUBND':'par_ubnd', 'PARGP': 'par_gp',
                                'SCALE':'scale','OFFSET':'offest','DERCOM':'dercom'}
        columns = ['PARNME', 'PARTIED']
        self.tied_parm = pd.DataFrame(columns=columns)


    def __read_template(self):
        fnc = os.path.join(os.path.dirname(__file__),"Control_default.txt")
        fid = open(fnc,'r')
        content = fid.readlines()
        fid.close()
        self.sections_dict = {}
        in_section = False
        for line in content:
            line = line.strip()
            if line =='pcf':
                self.header = line

            elif line[0]=='*': # section

                section_name = line[1:].strip()
                self.sections.append(section_name)
                in_section = True
                in_sec_ln_count = 0
                lines_dict = {}
            elif line[0]=='-':
                break
            elif in_section:
                in_sec_ln_count = in_sec_ln_count + 1
                line = line.strip()
                line = line.split(',')
                record = []
                for word in line:
                    ws_dict = {}
                    ws = word.split('=')
                    ws[0] = ws[0].replace("[","")
                    ws[1] = ws[1].replace("]", "")
                    ws_dict[ws[0]] = ws[1]
                    setattr(self, ws[0].strip(),ws[1].strip() )
                    record.append(ws_dict)

                lines_dict[in_sec_ln_count]= record
                self.sections_dict[section_name] = lines_dict

    def update_record(self):

        if self.PRECIS =="'$$'":
            self.PRECIS = 'single'
        if self.DPOINT == "'$$'":
            self.DPOINT == "point"
        # param group
        self.MParam.group_param
        gkeys = self.param_group_keys.keys()
        for kg in gkeys:
            att = self.param_group_keys[kg]
            val = self.MParam.group_param[att].values
            setattr(self,kg,val)

        # param data
        gkeys = self.param_data_keys.keys()
        for kg in gkeys:
            att = self.param_data_keys[kg]
            val = self.MParam.param_data[att].values
            setattr(self, kg, val)

        #
        self.NPAR = len(self.MParam.param_data)
        self.NOBS = len(self.MObser.obs_data)
        self.NPARGP = len(self.MParam.group_param)
        self.NOBSGP = len(self.MObser.group_obs)

        # update file names
        self.TEMPFLE = self.MParam.filename
        self.INSFLE = self.MObser.filename


    def write(self):
        self.update_record()
        fid = open(self.filename,'w')
        fid.write(self.header)
        fid.write("\n")
        for section in self.sections:
            self.write_section(fid, section)

        fid.close()

    def write_section(self,fid, section_name):
        fid.write("* {}\n".format(section_name))
        if not section_name in ['parameter groups', 'parameter data', 'observation data', 'observation groups']:
            lines = self.sections_dict[section_name]

            max_line_num = max(lines.keys())
            for n in range(1,max_line_num+1):
                curr_line = lines[n]
                for word in curr_line:
                    kword = word.keys()[0].strip()
                    attri = getattr(self,kword)
                    if not attri=="@":
                        fid.write("{} ".format(attri))

                fid.write("\n")

        if section_name == 'parameter groups':
            df = self.MParam.group_param
            for gi in range(len(df)):
                vals = df.loc[0].values
                for val in vals:

                    if not(val == None or pd.isnull(val)):
                        lin = str(val) + ' '
                        fid.write(lin)
                fid.write('\n')
        if section_name == 'parameter data':
            df = self.MParam.param_data
            for i in range(len(df)):
                vals = df.loc[i].values
                for val in vals:
                    if  not( val == None or pd.isnull(val)):
                        lin = str(val) + ' '
                        fid.write(lin)
                fid.write('\n')
        if section_name == "observation groups":
            df = self.MObser.group_obs
            for i in range(len(df)):
                vals = df.loc[i].values
                for val in vals:
                    if not(val == None or pd.isnull(val) ):
                        lin = str(val) + " "
                        fid.write(lin)
                fid.write('\n')
        if section_name == "observation data":
            df = self.MObser.obs_data
            for i in range(len(df)):
                vals = df.loc[i].values
                for val in vals:
                    if not(val == None or  pd.isnull(val)):
                        lin = str(val) + " "
                        fid.write(lin)
                fid.write('\n')




if __name__ == "__main__":
    # conductivity 10
    para = []
    for i in np.arange(10):
        para.append("HK_%d" % (i))

    # storativity 10
    for i in np.arange(10):
        para.append("SS_%d" % (i))

    # faults permebility
    for i in np.arange(7):
        para.append("FHB_cond_%d" % (i))

    # param
    temp_par = MParam()
    temp_par.filename = "yuc.tpl"
    temp_par.param_data = para
    temp_par.write_file()

    # obs
    # heads
    obs = []
    temp_obs = MObser()
    for i in np.arange(7):
        obs.append("HD%d" % (i))

    temp_obs.obs_data = obs
    temp_obs.obs_data['obs_val'] = np.random.rand()

    temp_obs.write_ins_file()

    cont = Control()
    cont.MParam = temp_par
    cont.MObser = temp_obs
    cont.write()
    pass



