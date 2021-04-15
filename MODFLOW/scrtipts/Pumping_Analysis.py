import os, sys
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import datetime
from scipy import interpolate
from matplotlib.backends.backend_pdf import PdfPages

def main():
    # decalre an object to hold all pumping related information
    pmp = RR_pumping()

    # Pumping data
    pmp.pumping_data = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Municipal_Pumping\Pumping_RR_SBworking(" \
                       r"07-18-2018).xlsx"
    pmp.gis_well_file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\master_well.shp"
    pmp.service_area_file = r"D:\Workspace\projects\RussianRiver\GIS\update_service_area.shp"
    pmp.model_domain = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\RussianRiver_Watershed_no_SRP.shp"
    pmp.population_shp = r"D:\Workspace\projects\RussianRiver\GIS\all_pop.shp"
    pmp.pop_service_area = r"D:\Workspace\projects\RussianRiver\GIS\all_pop_service_area.shp"
    pmp.hru_map = r"D:\Workspace\projects\RussianRiver\Climate_data\gis\hru_param_tzones.shp"
    pmp.weather_stations =  r"D:\Workspace\projects\RussianRiver\rr_model.git\PRMS\input\prms_rr.dat"
    pmp.stress_periods = pd.read_excel(r"D:\Workspace\projects\RussianRiver\modflow\other_files\budget.xlsx",
                                       sheet_name='time_dis')

    pmp.start_date = datetime.datetime(year=1990, month=1, day=1)
    pmp.end_date = datetime.datetime(year=2015, month=12, day=31)
    pmp.month_list = [i.strftime("%m-%y") for i in pd.date_range(start=pmp.start_date, end=pmp.end_date, freq='MS')]
    # Read shapefiles
    #pmp.service_area_df = gp.read_file(pmp.service_area_file)
    pmp.bcg_poly = gp.read_file(pmp.model_domain)
    pmp.wgis = gp.read_file(pmp.gis_well_file)
    #pmp.pop_gis = gp.read_file(r"D:\Workspace\projects\RussianRiver\GIS\all_pop.shp")
    pmp.hru_shp = gp.read_file(pmp.hru_map)
    pmp.pop_serice_df = gp.read_file(pmp.pop_service_area )

    # pmp.pop_weight_srvc_area()
    pmp.read_raw_pumping_data()
    pmp.compute_wells_general_info()
    # pmp.plot_missing_perc()
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

        # loop over all wells
        for id in self.sys_ids:
            loc = self.pmp_rate_df['System ID'].values == id
            curr_info = self.pmp_rate_df[loc]
            sys_id.append(id)
            sys_name.append(curr_info['System Name'].values[0])
            curr_arr = curr_info.values
            pp = curr_arr[:, 4:16].flatten()
            pp = pp.reshape((len(pp), 1)).astype(float)
            missing_perc.append(len(np.where(np.isnan(pp))[0]) / len(pp) * 100.0)
            ave.append(np.nanmean(pp))
            std.append(np.nanstd(pp))

            yy = curr_info['Year'].values
            nyears = len(yy)
            yy = np.tile(yy, (12, 1))
            yy = yy.T.flatten().reshape((np.size(yy), 1))
            mm = np.tile(np.arange(1, 13), (nyears, 1))
            mm = mm.flatten().reshape((np.size(mm), 1))
            pump_info[id] = np.hstack((yy, mm, pp))

        data = {'sys_id': sys_id, 'sys_name': sys_name, 'missing_perc': missing_perc,
                'ave': ave, 'std': std}
        self.wells_info = pd.DataFrame.from_dict(data)
        self.pumping_info = pump_info

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

        pass

    def estimate_pumping(self):

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
        #grouped = pd.groupby(self.pop_serice_df, 'pwsid')
        grouped = self.pop_serice_df.groupby(['pwsid'])
        # Loop over water systems
        water_sys_info = {}
        noData_water_sys = []
        for name, group in grouped:
            flg_compute = False
            print(name)
            if name == 0:
                continue
            try:
                # get active date
                #(self.pop_serice_df['activity_d'] != None) and (self.pop_serice_df['pwsid'] == name)
                A_dates = self.pop_serice_df['activity_d'][(self.pop_serice_df['activity_d'] != None)
                        & (self.pop_serice_df['pwsid'] == name)]
                active_date = A_dates.values[0]
                ayear, amon, aday = active_date.split("-")
                ayear = int(ayear)
                amon =  int(amon)
                curr_pump = self.pumping_info[name]
                curr_pump = curr_pump[curr_pump[:, 0] < 2016]
                if 1:
                    yy_mm = curr_pump[:, 0:2]
                    mask_active = yy_mm[:,0]<ayear
                    curr_pump = pd.DataFrame(curr_pump, columns=['year', 'month', 'flow'])
                    curr_pump = curr_pump.groupby(['year', 'month'])['flow'].apply(lambda x: x.sum(skipna=False))
                    curr_pump = curr_pump.values.reshape(len(curr_pump), 1)
                    if 0: # this is done becuase actiavtion date might be wrong
                        curr_pump[mask_active] = np.nan
                    curr_pump = np.hstack((yy_mm, curr_pump))
                flg_compute = True
            except:
                print("No pumping data ...")
                noData_water_sys.append(name)
            if flg_compute:

                curr_info = self.compute_avergae(group)
                w_sys_info = pd.DataFrame(curr_pump, columns=['Year', 'Month', 'PumpingRate'])
                w_sys_info['Pop_service'] = group['d_populati'].values[0]

                try:
                    w_sys_info['TEMP'] = curr_info['Temp.'].values
                    w_sys_info['POP'] = curr_info['pop']
                except:
                    pass
                water_sys_info[name] = w_sys_info
        if False: # plot raw data
            all_frames = []
            with PdfPages('pumping_info.pdf') as pdf:
                for wsys in water_sys_info.keys():
                    water_sys_info[wsys]['WS']  = wsys
                    all_frames.append(water_sys_info[wsys])
                    time = water_sys_info[wsys]['Year'] + water_sys_info[wsys]['Month']/12.0
                    fig1 = plt.plot(time, water_sys_info[wsys]['PumpingRate'])
                    plt.title(str(wsys))
                    pdf.savefig()
                    plt.close()
                    plt.figure()
                    fig2 = plt.plot(time, water_sys_info[wsys]['POP'])
                    plt.title(str(wsys))
                    pdf.savefig()
                    plt.close()
                    plt.figure()
                    qq = 325851 * (water_sys_info[wsys]['PumpingRate'] / water_sys_info[wsys]['POP'])/30.0
                    fig3 = plt.plot(time,qq)
                    plt.title(str(wsys))
                    pdf.savefig()
                    plt.close()
        # compute total pumping recorded
        if True:
            all_frames = []
            for wsys in water_sys_info.keys():
                water_sys_info[wsys]['WS'] = wsys
                all_frames.append(water_sys_info[wsys])
               # aa = water_sys_info[wsys]
                #aa = aa[aa['PumpingRate'] > 0]
                #all_frames.append(aa)
                #aa = aa.groupby(['Year']).mean()
                time = water_sys_info[wsys]['Year'] + water_sys_info[wsys]['Month'] / 12.0
                try:
                    plt.scatter(aa['TEMP'], aa['PumpingRate'],  cmap='Paired')
                except:
                    pass

            result = pd.concat(all_frames)
            result['PumpingRate'][result['PumpingRate'] <= 0] = np.nan
            result.to_csv("Pumping_temp_pop_Modfied.csv")
            aa = result.groupby(['Year', 'Month']).sum()

            qq = 325851 * (aa['PumpingRate'].values/aa['POP'].values)/30.0
            plt.plot(time, qq)

            pass
        # fill missing data

        result = pd.concat(all_frames)
        aa = result[result['POP']>1000]
        aa = aa[aa['PumpingRate']>0]
        xxx = 1












        pass


if __name__ == "__main__":
    main()
