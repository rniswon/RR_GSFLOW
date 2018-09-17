import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import prms_py
import datetime


class Budget(object):
    def __init__(self, prms_py):
         fn = prms_py.prms_control['model_output_file'][2][0]
         fparts = fn.split('/')
         wc = prms_py.work_directory
         self.work_directory = prms_py.work_directory
         wcparts = wc.split('\\')
         del(fparts[0])
         del(wcparts[-1])
         wc1 = '\\'.join(wcparts)
         fn2 = '\\'.join(fparts)
         self.budget_file = os.path.join(wc1,fn2)
         ##self.read_budget() # it is difficult to read budget file....

         ## read read intercept
         self.read_intercept_budget()
         self.plot_interc_budget()
         self.read_gw_budget()
         self.read_soilzone_budget()
         self.plot_soilzone_budget()

    def read_intercept_budget(self):
        wc = self.work_directory
        fn = "intcp.wbal"
        fn = os.path.join(wc,fn)
        header = ['Date', 'Water Bal', 'Precip', 'Netppt', 'Intcpevap', 'Intcpstor','last_stor', 'changeover']
        df = pd.read_csv(fn, names=header, skiprows=[0], delim_whitespace=True)
        dt = self.object_to_date(df.Date.values)
        df.Date = dt
        self.interc_budget = df


    def read_gw_budget(self):
        wc = self.work_directory
        fn = "gwflow.wbal"
        fn = os.path.join(wc,fn)
        header = [ 'Date', 'Water Bal',  'last store', 'GWR store',
                   'GW input',  'GW flow',    'GW sink',  'GW upslope', 'minarea_in',
                   'downflow']
        df = pd.read_csv(fn, names=header, skiprows=[0], delim_whitespace=True)
        dt = self.object_to_date(df.Date.values)
        df.Date = dt
        self.gw_budget = df

    def read_soilzone_budget(self):
        wc = self.work_directory
        fn = "soilzone.wbal"
        fn = os.path.join(wc, fn)
        header = [    'Date',     'Water Bal',     'bsmbal',    'last SM',  'soilmoist',  'last stor',
                      'SS stor',    'perv ET',     'sz2gw',  'interflow', 'soil2gw',  'dunnian',
                      'soil in',  'lakeinsz', 'downflow', 'swale ET',  'pref flow',   'pfr dunn',
                      'pfr stor',  'slow stor', 'dunnian gvr', 'lake evap']
        df = pd.read_csv(fn, names=header, skiprows=[0], delim_whitespace=True)
        dt = self.object_to_date(df.Date.values)
        df.Date = dt
        self.soilzone_budget = df

    def plot_soilzone_budget(self):
        header = ['Date', 'Water Bal', 'bsmbal', 'last SM', 'soilmoist', 'last stor',
                  'SS stor', 'perv ET', 'sz2gw', 'interflow', 'soil2gw', 'dunnian',
                  'soil in', 'lakeinsz', 'downflow', 'swale ET', 'pref flow', 'pfr dunn',
                  'pfr stor', 'slow stor', 'dunnian gvr', 'lake evap']
        lenn = len(header)-1
        df = self.soilzone_budget
        n = 0
        nm = 0
        fin = 0
        for i in np.arange(lenn):
            n = n + 1
            if n < 5:
                if n==1:
                    fin = fin + 1
                    plt.figure(fin)
            else:
                n = 1
                fin = fin + 1
                plt.figure(fin)

            plt.subplot(2,2,n)
            nm = nm + 1
            col_name = header[nm]
            plt.plot(df.Date.values, df[col_name].values)
            plt.xlabel('Date')
            plt.ylabel(col_name)
            plt.title(col_name)
        pass


    def plot_gw_budget(self):
        header = ['Date', 'Water Bal', 'last store', 'GWR store',
                  'GW input', 'GW flow', 'GW sink', 'GW upslope', 'minarea_in',
                  'downflow']
        plt.figure()
        df = self.gw_budget
        n = 0
        nm = 0
        fin = 0
        for i in np.arange(9):
            n = n + 1
            if n < 5:
                if n == 1:
                    fin = fin + 1
                    plt.figure(fin)
            else:
                n = 1
                fin = fin + 1
                plt.figure(fin)

            nm = nm + 1
            plt.subplot(3,3,n)
            col_name = header[nm]
            plt.plot(df.Date.values, df[col_name].values)
            plt.xlabel('Date')
            plt.ylabel(col_name)
            plt.title(col_name)
        plt.tight_layout()

    def plot_interc_budget(self):
        header = ['Date', 'Water Bal', 'Precip', 'Netppt', 'Intcpevap', 'Intcpstor','last_stor', 'changeover']

        df = self.interc_budget
        n = 0
        nm = 0
        fin = 0

        for i in np.arange(7):
            n = n + 1
            if n < 5:
                if n == 1:
                    fin = fin + 1
                    plt.figure(fin)
            else:
                n = 1
                fin = fin + 1
                plt.figure(fin)

            nm = nm + 1
            plt.subplot(2,2,n)
            col_name = header[nm]
            plt.plot(df.Date.values, df[col_name].values)
            plt.xlabel('Date')
            plt.ylabel(col_name)
            plt.title(col_name)



    def object_to_date(self, ob):
        dt = []
        for o in ob:
            line = o.split('/')
            yr = int(line[0])
            mo = int(line[1])
            dd = int(line[2])
            dt1 = datetime.datetime(year=yr, month=mo, day=dd)
            dt.append(dt1)
        return dt




    def read_budget(self):
        self.fid = open(self.budget_file, 'r')
        content = self.fid.readlines()
        self.fid.close()
        flg = 0
        record = []
        for line in content:
            print line
            keywords = line.split()

            if keywords[0] == 'Year':
                header = line.split()
            if flg == 1:
                if line[0:2]== ' *':
                    flg = 0
                else:
                    rec_parts = line.split()
                    if rec_parts[0] == 'initial':
                        pass
                    else:
                        rec_parts = [float(p) for p in rec_parts]
                        record.append(rec_parts)

            if line[0:2] == ' -':
                flg = 1

        pass



class Statistics(object):
    def __init__(self, prms_py):
        fn = prms_py.prms_control['stat_var_file'][2][0]
        # fparts = fn.split('/')
        # wc = prms_py.work_directory
        # self.work_directory = prms_py.work_directory
        # wcparts = wc.split('\\')
        # del (fparts[0])
        # del (wcparts[-1])
        # wc1 = '\\'.join(wcparts)
        # fn2 = '\\'.join(fparts)
        # self.statvar_file = os.path.join(wc1, fn2)
        self.statvar_file = fn
        self.read_stat_var()

    def read_stat_var(self):
        fid = open(self.statvar_file, 'r')
        num_var = int(fid.readline().strip())
        var_names = []
        var_elements = []
        for var in range(num_var):
            line = fid.readline()
            ws = line.split()
            var_names.append(ws[0])
            var_elements.append(int(ws[1]))

        data = fid.readlines()
        data_float = []
        for rec in data:
            rec = rec.strip()
            rec = rec.split()
            data_float.append(rec)

        data_float = np.array(data_float, dtype=float)

        self.stat_dict = dict()
        dates = np.copy(data_float[:, 0:7])
        dates = dates.astype('int')
        date_list = []
        for dat in dates:
            date_list.append(datetime.datetime(year=dat[1], month=dat[2], day=dat[3]))

        self.stat_dict['Date'] = date_list

        ii = 0
        for nm in var_names:
            nm = nm+ "_"+str(ii)
            ele = var_elements[ii]
            self.stat_dict[nm] = [{'ID':ele}, data_float[:,(7+ii)]]
            ii = ii + 1

        fid.close()

    def plot(self):

        for key in self.stat_dict.keys():
            if key != 'Date':
                xx = self.stat_dict['Date']
                yy = self.stat_dict[key][1]
                plt.figure()
                plt.plot(xx,yy)
                plt.xlabel('Date')
                plt.ylabel(key)
                tit = "ID #: " + str(self.stat_dict[key][0]['ID'])
                plt.title(tit)







class Animation(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    cname = "C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\windows\prms_rr.control"
    prms = prms_py.Prms_base()
    prms.control_file_name = cname
    prms.load_prms_project()

    #bud = Budget(prms)
    stat = Statistics(prms)
    stat.plot()
    plt.show()


    pass