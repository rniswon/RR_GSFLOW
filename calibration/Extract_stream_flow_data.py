import pandas as pd
import numpy as np
from gispy import shp
import datetime
import matplotlib.pyplot as plt

sf_shp = r"D:\Workspace\projects\RussianRiver\GIS\gaugues_hrus.shp"
sf_data = r"D:\Workspace\projects\RussianRiver\Data\StreamGuage\sf_daily"
sf_attrib = shp.get_attribute_table(sf_shp)


def compute_annual_stream_flow(curr_flow):
    date = curr_flow[:, 1]
    years = [int(dt.year) for dt in date]
    years = np.array(years)
    yr_unq = np.unique(years)
    yr_mean = []
    for yr in yr_unq:
        mask = years == yr
        flow = curr_flow[mask,2]
        mf = np.mean(flow)
        if yr < 2017:
            yr_mean.append([yr,mf])
    return np.array(yr_mean)

def compute_monthly_avaerg(curr_flow):
    date = curr_flow[:, 1]
    months = [int(dt.month) for dt in date]
    years = [int(dt.year) for dt in date]
    years = np.array(years)
    months = np.array(months)
    mo_mean = []
    for mo in np.arange(1,13):
        mask = np.logical_and(months == mo, years < 2017)
        flow = curr_flow[mask, 2]
        mf = np.mean(flow)
        mo_mean.append([mo, mf])

    return np.array(mo_mean)

# read stream flow file
if False:
    fid = open(sf_data, 'r')
    content = fid.readlines()
    flg = 0
    all_sfr_data = []
    for line in content:
        if line[0]=='#':
            pass
        elif flg>2:
            line = line.split()
            try:
                tim = datetime.datetime.strptime(line[2], '%Y-%m-%d')
                rec = [int(line[1]), tim, float(line[3])]
                all_sfr_data.append(rec)
            except:
                pass


            pass

        else:
            flg = flg + 1
            pass
    fid.close()
else:
    all_sfr_data = np.load('all_sfr_data.npy')

## -------------
stream_data = dict()
for st in sf_attrib['STAID']:
    loc = all_sfr_data[:,0] == int(st)
    curr_rec = all_sfr_data[loc,:]
    loc = curr_rec[:, 1] >= datetime.datetime(1990, 1, 1, 0, 0)
    curr_rec = curr_rec[loc,:]

    plt.plot(curr_rec[:,1], curr_rec[:,2])
    plt.show()

    # current hru
    hru_id = sf_attrib['HRU_ID'].values[sf_attrib['STAID'] == st]
    ann_flow = compute_annual_stream_flow(curr_rec)
    mon_flow = compute_monthly_avaerg(curr_rec)
    stream_data[hru_id] = [ann_flow, mon_flow]
    pass


pass