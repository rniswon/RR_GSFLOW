import os, sys
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import datetime
from scipy import interpolate
from matplotlib.backends.backend_pdf import PdfPages
"""

"""
def main():
    # decalre an object to hold all pumping related information
    pmp = RR_pumping()

    # Pumping data
    # this file is corrected by Sandra for some errors in Sonoma County water use
    pmp.pumping_data = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Municipal_Pumping\Pumping_RR_SBworking(" \
                       r"07-18-2018)_corrected.xlsx"
    pmp.gis_well_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_wells2.shp"
    pmp.service_area_file = r"D:\Workspace\projects\RussianRiver\GIS\update_service_area.shp"
    pmp.model_domain = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\RussianRiver_Watershed_no_SRP.shp"
    pmp.population_shp = r"D:\Workspace\projects\RussianRiver\GIS\all_pop.shp"
    pmp.pop_service_area = r"D:\Workspace\projects\RussianRiver\GIS\all_pop_service_area.shp"
    pmp.hru_map = r"D:\Workspace\projects\RussianRiver\Climate_data\gis\hru_param_tzones.shp"
    pmp.weather_stations =  r"D:\Workspace\projects\RussianRiver\rr_model.git\PRMS\input\prms_rr.dat"
    pmp.stress_periods = pd.read_excel(r"D:\Workspace\projects\RussianRiver\modflow\other_files\budget.xlsx",
                                       sheet_name='time_dis')
    pmp.ws_database = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Public Potable Water Systems "
                                  r"FINAL 06-22-2018_0.csv")
    pmp.santa_rosa_pop = [113313, 147595, 168062]
    pmp.start_date = datetime.datetime(year=1990, month=1, day=1)
    pmp.end_date = datetime.datetime(year=2015, month=12, day=31)
    pmp.month_list = [i.strftime("%m-%y") for i in pd.date_range(start=pmp.start_date, end=pmp.end_date, freq='MS')]

    # Read shapefiles
    pmp.bcg_poly = gp.read_file(pmp.model_domain)
    pmp.wgis = gp.read_file(pmp.gis_well_file)
    pmp.wgis = pmp.wgis[pmp.wgis['Lat']>0 ]
    pmp.hru_shp = gp.read_file(pmp.hru_map)
    pmp.pop_serice_df = gp.read_file(pmp.pop_service_area )

    pmp.read_raw_pumping_data()
    #pmp.compute_wells_general_info()
    pmp.estimate_pumping()
    pass


class RR_pumping(object):
    def __init__(self):
        self.block_fshps = {}
        self.cencus_data_fn = {}

    def compute_wells_general_info(self):
        ## join
        self.wgis['System_ID'] = self.wgis['System'].values.astype(int)
        missing_sys = []
        ave = np.zeros_like(self.wgis['System_ID'].values, dtype=float)
        df_well_info = self.wells_info.groupby(['sys_id']).mean()
        df_well_info['sys_id'] = df_well_info.index
        new_df = self.wgis.join(df_well_info.set_index('sys_id'), on='System_ID')

        for i, sys_id in enumerate(self.wells_info['sys_id'].values):
            loc = self.wgis['System_ID'] == sys_id
            nwells = np.sum(loc)
            if nwells > 0:
                val = self.wells_info['ave'].values[i]  ##
                val = np.average(val)
                ave[loc] = val
            else:
                missing_sys.append(sys_id)

        self.wgis['missing_perc'] = ave


    def read_raw_pumping_data(self):
        """
        Reads the main pumping well file
        :return:
        Data frame
        """
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
        self.pmp_rate_df = pd.read_excel(self.pumping_data, sheet_name="monthly data (AF)")
        locc = self.pmp_rate_df['Unit'] != 'AF'
        self.pmp_rate_df.ix[locc, months] = np.nan
        self.sys_ids = np.unique(self.pmp_rate_df['System ID'].values)

        sys_id = []
        sys_name = []
        pump_info = {}
        missing_perc = []
        ave = []
        std = []
        df_pumping = []
        # loop over all wells
        for id in self.sys_ids:
            loc = self.pmp_rate_df['System ID'].values == id
            curr_info = self.pmp_rate_df[loc]
            if len(curr_info)> 27:
                sub_sys = curr_info['System Name'].unique()
                sub_sys = sub_sys.astype(str)
                sub_sys = sub_sys.tolist()
                sub_sys.remove('nan')

                pump_info = np.split(curr_info.values, int(len(curr_info)/27))
                temp_list = []
                for mat in pump_info:
                    temp_list.append(pd.DataFrame(mat, columns=curr_info.columns))
                pump_info = temp_list
            else:
                pump_info = [curr_info]

            for ppm in pump_info:
                try:
                    name = ppm['System Name'].values[0]
                except:
                    xxx = 1
                curr_arr = ppm.values
                pp = curr_arr[:, 4:16].flatten()
                pp = pp.reshape((len(pp), 1)).astype(float)
                yy = ppm['Year'].values
                nyears = len(yy)
                yy = np.tile(yy, (12, 1))
                yy = yy.T.flatten().reshape((np.size(yy), 1))
                mm = np.tile(np.arange(1, 13), (nyears, 1))
                mm = mm.flatten().reshape((np.size(mm), 1))
                pmp_info = np.hstack((yy, mm, pp))
                pmp_info = pd.DataFrame(pmp_info, columns=['Year', 'Month', 'Pumping'])
                pmp_info['Name'] = name
                pmp_info['WS'] = id
                df_pumping.append(pmp_info)


        self.pumping_info = pd.concat(df_pumping)

    def plot_missing_perc(self):
        bcg = self.bcg_poly.plot(color='white', edgecolor='black')
        fig1 = self.wgis.plot(ax=bcg, column='missing_perc', colormap='jet', legend=True)
        plt.tight_layout()
        plt.title("Percentage of missing Data (%)")
        plt.show()

    def pop_weight_srvc_area(self):
        """
        Find population weight for each service area
        """
        self.service_area_df['pwsid'] = self.service_area_df['pwsid'].str[2:].astype('int')

    def compute_avergae(self, group):
        s1 = pd.merge(self.hru_shp, group, how='inner', on=['HRU_ID'])
        s1 = s1.drop_duplicates('HRU_ID')

        # population
        pops = ['B_POP1990', 'B_POP2000','B_POP2010']
        x_old = [1,121,241]
        y_old = []
        for pop in pops:
            y_old.append(np.sum(s1[pop].values))
        f = interpolate.interp1d(x_old, y_old, fill_value="extrapolate")
        xnew = self.stress_periods['No.'].values
        ynew = f(xnew)
        service_area_population = ynew

        #temp
        # station hrus
        st_hru = {1:73774, 2:24089, 3:39556, 4:94037}
        temp = []
        stat_id = s1['TZONES'].values
        counts = np.bincount(stat_id)  # find most_frequent station
        stat_id = np.argmax(counts)
        try:
            cur_st_hru = st_hru[stat_id]
        except:
            pass
        curr_stat = self.hru_shp[self.hru_shp['HRU_ID'] == cur_st_hru]
        st_mean = []
        for m in range(12):
            tmax = "TMAX_" + str(m+1).zfill(2)
            tmin = "TMIN_" + str(m + 1).zfill(2)
            t_mean = 0.5 * s1[tmax].values + 0.5 * s1[tmin].values
            temp.append(np.mean(t_mean))
            st_mean.append(0.5 * curr_stat[tmax].values + 0.5 * curr_stat[tmin].values)
        stat_id = stat_id - 1
        ratio = np.mean(np.array(temp)/np.array(st_mean).T)
        ttmax = 'tmax_' + str(stat_id)
        ttmin = 'tmin_' + str(stat_id)
        MonthlyWeather = self.weather_data.groupby(['Year', 'Month']).mean()
        tav = ratio * (0.5 * MonthlyWeather[ttmax] + 0.5 * MonthlyWeather[ttmin])
        plt.plot(service_area_population)
        return {'Temp.':tav, 'pop':service_area_population}


    def compute_avergae_at_point(self, well):
        try:
            ws = 'CA' + str(int(well['System'].values))
        except:
            ws = 'CA' + str(int(well['System'].values[0]))
            aaa = 1

        well_pop = self.ws_database[self.ws_database['Water System No '] == ws]
        pop1 = well_pop['Total Population'].values[0]
        # population
        pops = ['B_POP1990', 'B_POP2000','B_POP2010']
        xnew = self.stress_periods['No.'].values
        ynew =np.zeros_like(xnew) + pop1
        service_area_population = ynew

        #temp
        # station hrus
        st_hru = {1:73774, 2:24089, 3:39556, 4:94037}
        temp = []
        stat_id = well['TZONES'].values
        counts = np.bincount(stat_id)  # find most_frequent station
        stat_id = np.argmax(counts)
        try:
            cur_st_hru = st_hru[stat_id]
        except:
            pass
        curr_stat = self.hru_shp[self.hru_shp['HRU_ID'] == cur_st_hru]
        st_mean = []
        for m in range(12):
            tmax = "TMAX_" + str(m+1).zfill(2)
            tmin = "TMIN_" + str(m + 1).zfill(2)
            t_mean = 0.5 * well[tmax].values + 0.5 * well[tmin].values
            temp.append(np.mean(t_mean))
            st_mean.append(0.5 * curr_stat[tmax].values + 0.5 * curr_stat[tmin].values)
        stat_id = stat_id - 1
        ratio = np.mean(np.array(temp)/np.array(st_mean).T)
        ttmax = 'tmax_' + str(stat_id)
        ttmin = 'tmin_' + str(stat_id)
        MonthlyWeather = self.weather_data.groupby(['Year', 'Month']).mean()
        tav = ratio * (0.5 * MonthlyWeather[ttmax] + 0.5 * MonthlyWeather[ttmin])
        #plt.plot(service_area_population)
        return {'Temp.':tav, 'pop':service_area_population}

        pass

    def estimate_pumping(self):

        # obtain a unique list of all ws in the study area
        ws1 = self.pop_serice_df['pwsid'].unique().tolist()
        ws2 = self.wgis['System'].unique().astype(int).tolist()
        ws3 = self.pumping_info['WS'].unique().tolist()
        ws4 = self.ws_database['Water System No '].unique().astype(str).tolist()
        ws4.remove('nan')
        ws4_ = []
        for s in ws4:
            ws4_.append(int(s[2:]))
        ws4 = ws4_
        all_ws = set(ws1) | set(ws2) | set(ws3)

        # read weather data
        fid = open(self.weather_stations, 'r')
        ws_nm = ['Year', 'Month', 'Day', 't1', 't2', 't3']
        linse_to_skip = 0
        while True:
            line = fid.readline()
            linse_to_skip += 1
            if 'tmin' in line or 'tmax' in line or 'precip' in line or 'runoff' in line:
                if '#' in line:
                    break
                vars = line.strip().split()
                for i in range(int(vars[1])):
                    nm = vars[0] + "_" + str(i)
                    ws_nm.append(nm)
        fid.close()
        self.weather_data = pd.read_csv(self.weather_stations, skiprows=linse_to_skip, names=ws_nm, delim_whitespace = True)

        ####
        No_service_Area = []
        all_training = []
        for water_sys in all_ws:
            if water_sys == 0:
                continue

            if water_sys in ws3:# check if there is any pumping data for the system
                print(water_sys)
                curr_pump = self.pumping_info[self.pumping_info['WS']==water_sys]
                curr_pump = curr_pump[curr_pump.Year < 2016]

                # check if this water system has spatial information
                group = self.pop_serice_df[self.pop_serice_df['pwsid'] == water_sys]
                names = curr_pump['Name'].unique().tolist()
                for sub_system in names:
                    pump_info = curr_pump[curr_pump['Name'] == sub_system]
                    if len(group) > 0:
                        curr_info = self.compute_avergae(group)
                        w_sys_info = pump_info.copy()
                        w_sys_info['Pop_service'] = group['d_populati'].values[0]
                        w_sys_info['TEMP'] = curr_info['Temp.'].values
                        w_sys_info['POP'] = curr_info['pop']
                        w_sys_info['WS'] = water_sys
                        try:
                            w_sys_info['Name'] = pump_info['Name'].values[0]
                        except:
                            xxx = 1
                        all_training.append(w_sys_info)
                    elif water_sys in ws4 and water_sys in ws2:
                        w_sys_info = pump_info.copy()
                        well_info = self.wgis[self.wgis['System'] == water_sys]
                        curr_info = self.compute_avergae_at_point(well_info)
                        w_sys_info['Pop_service'] = curr_info['pop'][0]
                        try:
                            w_sys_info['TEMP'] = curr_info['Temp.'].values
                        except:
                            cc = 1
                        try:
                            w_sys_info['POP'] = curr_info['pop']
                        except:
                            ccc = 1

                        w_sys_info['WS'] = water_sys
                        w_sys_info['Name'] = pump_info['Name'].values[0]
                        all_training.append(w_sys_info)

                        pass
                    else:
                        No_service_Area.append(water_sys)

                    if 0 :
                        continue
                        print("******* No spatial information is available in service area, try wells file")
                        if water_sys in ws2:
                            well_info = self.wgis[self.wgis['System']==water_sys]
                            self.compute_avergae_at_point(well_info)
                            pass
                        else:
                            print("***** Cannot find a location of this water system ****** ")


                    pass

            else:
                print ("No pumping data is available .....")


        all_training = pd.concat(all_training)
        all_training.to_csv("Pumping_temp_pop.csv")


if __name__ == "__main__":
    main()
