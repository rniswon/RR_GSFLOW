# import packages ------------------------------------------------------------------------------------####
import sys, os
import flopy
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from datetime import datetime, timedelta
import seaborn as sns
from flopy.utils.geometry import Polygon, LineString, Point
from flopy.export.shapefile_utils import recarray2shp, shp2recarray


# settings ------------------------------------------------------------------------------------####

# input file directory (i.e. directory containing mf name file)
input_dir = r"..\..\windows"

# K zone input file
K_zone_file = r".\input_data\K_zone_ids.dat"

# subbasin input file
subbasins_file = r".\input_data\hru_shp.csv"

# output file directory (i.e. directory containing mf name file)
output_dir_plots = r"..\..\checks\check_obs_wells\plots"
output_dir_tables = r"..\..\checks\check_obs_wells\tables"
output_dir_gis = r"..\..\checks\check_obs_wells\gis"

# set file names
mf_name_file = os.path.join(input_dir, "rr_tr.nam")

# set coordinate system offset from bottom left corner of model grid
xoff = 465900
yoff = 4238400
epsg = 26910

# set options
plot_wells_indiv = 0
plot_wells_group = 0
create_data_frame_with_dates = 0
create_mean_water_level_shapefile = 0
create_shapefile_of_layer_elev = 1
create_shapefile_of_K_zones = 1
create_shapefile_of_subbasins = 1
create_shapefile_of_ponds = 0
create_shapefile_of_wells = 0


# read in transient model files -----------------------------------------------------------------------####

mf = flopy.modflow.Modflow.load("rr_tr.nam", "mfnwt", model_ws = os.path.dirname(mf_name_file), load_only=['HOB'])
hob = mf.get_package('HOB')



# plot well timeseries: individually -----------------------------------------------------------------------####

if plot_wells_indiv == 1:

    # set well IDs to examine
    obs_well_ids = ["HO_23", "HO_37", "HO_24", "HO_20",
                    "HO_142", "HO_151", "HO_150", "HO_162",
                    "HO_145", "HO_139", "HO_140", "HO_158",
                    "HO_159", "HO_160", "HO_128", "HO_125",
                    "HO_123", "HO_122", "HO_130", "HO_155",
                    "HO_156", "HO_157", "HO_73", "HO_80",
                    "HO_76", "HO_87", "HO_91", "HO_93",
                    "HO_96", "HO_66", "HO_48", "HO_16",
                    "HO_32", "HO_14", "HO_0",
                    "HO_11", "HO_1", "HO_7"]
    obs_well_ids_num = [23, 37, 24, 20,
                        142, 151, 150, 162,
                        145, 139, 140, 158,
                        159, 160, 128, 125,
                        123, 122, 130, 155,
                        156, 157, 73, 80,
                        76, 87, 91, 93,
                        96, 66, 48, 16,
                        32, 14, 0,
                        11, 1, 7]

    # loop through selected wells and plot time series
    for i in obs_well_ids_num:

        # get hob object for selected observation well
        this_hob = hob.obs_data[i]

        # get hob id
        # TODO: make this more general, this only works because the HOB ids match up with the python indices
        this_hob_id = this_hob.obsname

        # create date list
        model_time = this_hob.time_series_data["totim"] + this_hob.time_series_data["toffset"]
        model_time = model_time - 1
        model_time = model_time.tolist()
        model_time = [int(x) for x in model_time]
        start_date = datetime(1990, 1, 1)
        date_list = [start_date + timedelta(days=x) for x in model_time]

        # create data frame
        data = {'date': date_list, 'heads': this_hob.time_series_data["hobs"]}
        df = pd.DataFrame(data)

        # plot and export
        # TODO: create a month column and shade if it is the wet season
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(df['date'], df['heads'])
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_title("Time series: " + this_hob_id + ", layer " + str(this_hob.layer + 1))
        ax.set_xlabel('Date')
        ax.set_ylabel('Head (m)')
        ax.grid(True)
        plt.tight_layout()
        file_name = "head_time_series_" + this_hob_id + ".jpg"
        file_path = os.path.join(output_dir_plots, file_name)
        plt.savefig(file_path)





# plot well timeseries: groups -----------------------------------------------------------------------####

if plot_wells_group == 1:

    # identify wells to plot in group - build dictionary
    well_group_dict = {"group_01": [142, 147, 141, 143],
                       "group_02": [151, 150, 141, 166],
                       "group_03": [162, 145, 144, 148, 149, 139, 140],
                       "group_04": [139, 140, 135, 144, 145],
                       "group_05": [158, 159, 160, 128, 127],
                       "group_06": [123, 122, 125, 127, 161, 128, 158, 159, 160],
                       "group_07": [130, 135, 158, 159, 160, 154, 155, 156, 157],
                       "group_08": [155, 156, 157, 152, 153, 130],
                       "group_09": [73, 76, 80, 115, 116, 118, 83, 82, 74, 75, 81],
                       "group_10": [87, 91, 88, 89, 90, 92, 93, 83, 85],
                       "group_11": [93, 87, 88, 89, 91, 90, 92, 85, 83],
                       "group_12": [96, 94, 95, 97],
                       "group_13": [66, 64, 68, 94],
                       "group_14": [48, 64, 47],
                       "group_15": [16, 43, 31],
                       "group_16": [14, 15, 5, 12, 30],
                       "group_17": [32, 18, 19, 33],
                       "group_18": [23, 37, 24, 20],
                       "group_19": [0, 5, 17, 3],
                       "group_20": [11, 3, 10, 17],
                       "group_21": [1, 7, 0, 2, 3, 4, 5],
                       "group_22": [7, 2, 6, 8, 9]}

    # define function to plot well groups
    def plot_well_groups(well_group_name, well_group_ids):

        # prep well ids
        obs_well_ids_num = well_group_ids
        obs_well_ids = [str(int) for int in obs_well_ids_num]
        obs_well_ids = ["HO_" + e for e in obs_well_ids]

        # loop through selected wells and plot time series
        df_list = []
        c=0
        for i in obs_well_ids_num:

            # get hob object for selected observation well
            # TODO: make this more general, this only works because the HOB ids match up with the python indices
            this_hob = hob.obs_data[i]

            # get hob id
            #this_hob_id = this_hob.obsname

            # create date list
            model_time = this_hob.time_series_data["totim"] + this_hob.time_series_data["toffset"]
            model_time = model_time - 1
            model_time = model_time.tolist()
            model_time = [int(x) for x in model_time]
            start_date = datetime(1990, 1, 1)
            date_list = [start_date + timedelta(days=x) for x in model_time]

            # create data frame and store in list
            data = {'site': obs_well_ids[c], 'date': date_list, 'heads': this_hob.time_series_data["hobs"]}
            df = pd.DataFrame(data)
            df_list.append(df)

            # update counter
            c = c+1


        # create data frame of all sites
        df = pd.concat(df_list)

        # decide on number of columns in plot, depending on number of sites being plotted
        if len(well_group_ids) <= 4:
            col_wrap_val = 2
        elif len(well_group_ids) <= 9:
            col_wrap_val = 3
        elif len(well_group_ids) > 9:
            col_wrap_val = 4

        # plot group of sites and export
        # TODO: create a month column and shade if it is the wet season?
        p = sns.relplot(data=df, x="date", y="heads", col="site", col_wrap=col_wrap_val)
        p.set_xticklabels(rotation=45)
        plt.tight_layout()
        file_name = "head_time_series_" + well_group_name + ".jpg"
        file_path = os.path.join(output_dir_plots, file_name)
        plt.savefig(file_path)
        plt.close()

    # loop through well_group_dict and plot
    for well_group_name, well_group_ids in well_group_dict.items():
        plot_well_groups(well_group_name, well_group_ids)





# create HOB data frame with dates -----------------------------------------------------------------------####

if create_data_frame_with_dates == 1:

    # create HOB well ids
    obs_well_ids_num = list(range(0,171))
    obs_well_ids = [str(int) for int in obs_well_ids_num]
    obs_well_ids = ["HO_" + e for e in obs_well_ids]

    # loop through wells
    df_list = []
    for i in obs_well_ids_num:

        # get hob object for selected observation well
        # TODO: make this more general, this only works because the HOB ids match up with the python indices
        this_hob = hob.obs_data[i]

        # create date list
        model_time = this_hob.time_series_data["totim"] + this_hob.time_series_data["toffset"]
        model_time = model_time - 1
        model_time = model_time.tolist()
        model_time = [int(x) for x in model_time]
        start_date = datetime(1990, 1, 1)
        date_list = [start_date + timedelta(days=x) for x in model_time]

        # create data frame and store in list
        data = {'site': obs_well_ids[i], 'date': date_list, 'heads': this_hob.time_series_data["hobs"]}
        df = pd.DataFrame(data)
        df_list.append(df)


    # create data frame of all sites
    df = pd.concat(df_list)

    # write csv
    file_name = "HOB_obs_transient.csv"
    file_path = os.path.join(output_dir_tables, file_name)
    df.to_csv(file_path, index=False)





# create mean water level shapefile -----------------------------------------------------------------------####

if create_mean_water_level_shapefile == 1:

    # create data frame with mean water level during selected time periods ------------------------------####
    # dry season (May-October) - 1/1/1990 - 12/31/2015
    # dry season (May-October) - 1/1/1990 - 12/31/2002
    # dry season (May-October) - 1/1/2003 - 12/31/2015
    # wet season (Nov-April) - 1/1/1990 - 12/31/2015
    # wet season (Nov-April) - 1/1/1990 - 12/31/2002
    # wet season (Nov-April) - 1/1/2003 - 12/31/2015

    # create HOB well ids
    obs_well_ids_num = list(range(0, 171))
    obs_well_ids = [str(int) for int in obs_well_ids_num]
    obs_well_ids = ["HO_" + e for e in obs_well_ids]

    # loop through wells
    df_list = []
    well_loc = []
    for i in obs_well_ids_num:
        # get hob object for selected observation well
        # TODO: make this more general, this only works because the HOB ids match up with the python indices
        this_hob = hob.obs_data[i]

        # create date list
        model_time = this_hob.time_series_data["totim"] + this_hob.time_series_data["toffset"]
        model_time = model_time - 1
        model_time = model_time.tolist()
        model_time = [int(x) for x in model_time]
        start_date = datetime(1990, 1, 1)
        date_list = [start_date + timedelta(days=x) for x in model_time]

        # store well location data
        # note: not subtracting one from row and column because already stored with internally adjusted values in flopy
        well_loc.append([this_hob.obsname, this_hob.row, this_hob.column, this_hob.roff, this_hob.coff])

        # create data frame and store in list
        data = {'site': obs_well_ids[i], 'date': date_list, 'heads': this_hob.time_series_data["hobs"]}
        df = pd.DataFrame(data)
        df_list.append(df)


    # create data frame of well location data
    well_loc_df = pd.DataFrame(well_loc, columns=['obsname', 'row', 'col', 'roff', 'coff'])

    # create data frame of all sites
    df = pd.concat(df_list)

    # filter df by dates
    df_1990_2015 = df
    df_1990_2015_may_oct = df[df['date'].dt.month.isin(range(5,11))]
    df_1990_2015_nov_apr = df[df['date'].dt.month.isin([11,12,1,2,3,4])]      # have to do 11 instead of 10 because range is not inclusive
    df_1990_2002 = df[(df['date'] >= '1990-01-01') & (df['date'] <= '2002-12-31')]
    df_1990_2002_may_oct = df_1990_2002[df_1990_2002['date'].dt.month.isin(range(5,11))]
    df_1990_2002_nov_apr = df_1990_2002[df_1990_2002['date'].dt.month.isin([11,12,1,2,3,4])]
    df_2003_2015 = df[(df['date'] >= '2003-01-01') & (df['date'] <= '2015-12-31')]
    df_2003_2015_may_oct = df_2003_2015[df_2003_2015['date'].dt.month.isin(range(5,11))]     # have to do 11 instead of 10 because range is not inclusive
    df_2003_2015_nov_apr = df_2003_2015[df_2003_2015['date'].dt.month.isin([11,12,1,2,3,4])]

    # calculate mean for each site
    df_1990_2015 = df_1990_2015.groupby(['site'])['heads'].mean().reset_index()
    df_1990_2015_may_oct = df_1990_2015_may_oct.groupby(['site'])['heads'].mean().reset_index()
    df_1990_2015_nov_apr = df_1990_2015_nov_apr.groupby(['site'])['heads'].mean().reset_index()
    df_1990_2002 = df_1990_2002.groupby(['site'])['heads'].mean().reset_index()
    df_1990_2002_may_oct = df_1990_2002_may_oct.groupby(['site'])['heads'].mean().reset_index()
    df_1990_2002_nov_apr = df_1990_2002_nov_apr.groupby(['site'])['heads'].mean().reset_index()
    df_2003_2015 = df_2003_2015.groupby(['site'])['heads'].mean().reset_index()
    df_2003_2015_may_oct = df_2003_2015_may_oct.groupby(['site'])['heads'].mean().reset_index()
    df_2003_2015_nov_apr = df_2003_2015_nov_apr.groupby(['site'])['heads'].mean().reset_index()

    # get well ids for each data frame
    sites_df_1990_2015 = df_1990_2015['site'].str.split('_').str[1].tolist()
    sites_df_1990_2015_may_oct = df_1990_2015_may_oct['site'].str.split('_').str[1].tolist()
    sites_df_1990_2015_nov_apr = df_1990_2015_nov_apr['site'].str.split('_').str[1].tolist()
    sites_df_1990_2002 = df_1990_2002['site'].str.split('_').str[1].tolist()
    sites_df_1990_2002_may_oct = df_1990_2002_may_oct['site'].str.split('_').str[1].tolist()
    sites_df_1990_2002_nov_apr = df_1990_2002_nov_apr['site'].str.split('_').str[1].tolist()
    sites_df_2003_2015 = df_2003_2015['site'].str.split('_').str[1].tolist()
    sites_df_2003_2015_may_oct = df_2003_2015_may_oct['site'].str.split('_').str[1].tolist()
    sites_df_2003_2015_nov_apr = df_2003_2015_nov_apr['site'].str.split('_').str[1].tolist()

    # # convert well ids to integer
    sites_df_1990_2015 = list(map(int, sites_df_1990_2015))
    sites_df_1990_2015_may_oct = list(map(int, sites_df_1990_2015_may_oct))
    sites_df_1990_2015_nov_apr = list(map(int, sites_df_1990_2015_nov_apr))
    sites_df_1990_2002 = list(map(int, sites_df_1990_2002))
    sites_df_1990_2002_may_oct = list(map(int, sites_df_1990_2002_may_oct))
    sites_df_1990_2002_nov_apr = list(map(int, sites_df_1990_2002_nov_apr))
    sites_df_2003_2015 = list(map(int, sites_df_2003_2015))
    sites_df_2003_2015_may_oct = list(map(int, sites_df_2003_2015_may_oct))
    sites_df_2003_2015_nov_apr = list(map(int, sites_df_2003_2015_nov_apr))



    # create and export shapefile -------------------------------------------------------------####

    # set coordinate system information
    mf.modelgrid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)

    # grab coordinate data for each well
    coord_row = mf.modelgrid.get_ycellcenters_for_layer(0)
    coord_col = mf.modelgrid.get_xcellcenters_for_layer(0)

    # loop through well_loc_df
    cell_size = 300     # TODO: should grab this from mf object instead of assigning number
    geoms = []
    for row, col, roff, coff in zip(well_loc_df['row'], well_loc_df['col'], well_loc_df['roff'], well_loc_df['coff']):

        # grab coordinate data for each well
        this_coord_row = coord_row[row, col]
        this_coord_col = coord_col[row, col]

        # adjust for roff and coff
        this_coord_row_actual = this_coord_row + (-1*(cell_size * roff))  # multiplying by -1 because roff is negative as you move up but the UTM grid is positive as you move up
        this_coord_col_actual = this_coord_col + (cell_size * coff)

        # store geoms
        geoms.append(Point(this_coord_col_actual, this_coord_row_actual))  # may need to add 0 as last argument, but default value of has_z=0 may not require it


    # create recarray
    df_1990_2015 = df_1990_2015.to_records()
    df_1990_2015_may_oct = df_1990_2015_may_oct.to_records()
    df_1990_2015_nov_apr = df_1990_2015_nov_apr.to_records()
    df_1990_2002 = df_1990_2002.to_records()
    df_1990_2002_may_oct = df_1990_2002_may_oct.to_records()
    df_1990_2002_nov_apr = df_1990_2002_nov_apr.to_records()
    df_2003_2015 = df_2003_2015.to_records()
    df_2003_2015_may_oct = df_2003_2015_may_oct.to_records()
    df_2003_2015_nov_apr = df_2003_2015_nov_apr.to_records()


    # create and export shapefiles
    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2015.shp")
    recarray2shp(df_1990_2015, [geoms[i] for i in sites_df_1990_2015], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2015_may_oct.shp")
    recarray2shp(df_1990_2015_may_oct, [geoms[i] for i in sites_df_1990_2015_may_oct], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2015_nov_apr.shp")
    recarray2shp(df_1990_2015_nov_apr, [geoms[i] for i in sites_df_1990_2015_nov_apr], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2002.shp")
    recarray2shp(df_1990_2002, [geoms[i] for i in sites_df_1990_2002], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2002_may_oct.shp")
    recarray2shp(df_1990_2002_may_oct, [geoms[i] for i in sites_df_1990_2002_may_oct], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_1990_2002_nov_apr.shp")
    recarray2shp(df_1990_2002_nov_apr, [geoms[i] for i in sites_df_1990_2002_nov_apr], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_2003_2015.shp")
    recarray2shp(df_2003_2015, [geoms[i] for i in sites_df_2003_2015], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_2003_2015_may_oct.shp")
    recarray2shp(df_2003_2015_may_oct, [geoms[i] for i in sites_df_2003_2015_may_oct], shpname=shapefile_path, epsg=epsg)

    shapefile_path = os.path.join(output_dir_gis, "mean_obs_water_level_2003_2015_nov_apr.shp")
    recarray2shp(df_2003_2015_nov_apr, [geoms[i] for i in sites_df_2003_2015_nov_apr], shpname=shapefile_path, epsg=epsg)




# create shapefile of layer elevations (and other model attributes) -----------------------------------------------------------------------####

if create_shapefile_of_layer_elev == 1:

    # read in modflow files
    input_dir_ss = r"..\..\..\MODFLOW\ss"
    mf_name_file_ss = os.path.join(input_dir_ss, "rr_ss.nam")
    mf_ss = flopy.modflow.Modflow.load("rr_ss.nam", "mfnwt", model_ws=os.path.dirname(mf_name_file_ss))

    # set spatial reference info
    xll = 465900
    yll = 4238400
    epsg=26910
    mf_ss.modelgrid.set_coord_info(xoff=xll, yoff=yll, epsg=epsg)

    # create shapefile
    file_name = "rr_ss_model_attributes.shp"
    file_path = os.path.join(output_dir_gis, file_name)
    flopy.export.shapefile_utils.model_attributes_to_shapefile(file_path, mf_ss)




# create shapefile of subbasins ----------------------------------------------------------------------------------####

if create_shapefile_of_subbasins == 1:

    # read in modflow files
    input_dir_ss = r"..\..\..\MODFLOW\ss"
    mf_name_file_ss = os.path.join(input_dir_ss, "rr_ss.nam")
    mf_ss = flopy.modflow.Modflow.load("rr_ss.nam", "mfnwt", model_ws=os.path.dirname(mf_name_file_ss))

    # read in subbasin file
    subbasins = pd.read_csv(subbasins_file)

    # create array dict
    num_row = mf_ss.nrow
    num_col = mf_ss.ncol
    subbasin_array = subbasins[["subbasin"]].to_numpy().reshape(num_row, num_col)
    array_dict = {"subbasin": subbasin_array}

    # set spatial reference info
    xll = 465900
    yll = 4238400
    epsg=26910
    mf_ss.modelgrid.set_coord_info(xoff=xll, yoff=yll, epsg=epsg)

    # create shapefile
    file_name = "subbasins_hru.shp"
    file_path = os.path.join(output_dir_gis, file_name)
    flopy.export.shapefile_utils.write_grid_shapefile(file_path, mf_ss.modelgrid, array_dict, nan_val=-999.98999)




# create shapefile of K zones ----------------------------------------------------------------------------------####

if create_shapefile_of_K_zones == 1:

    # read in modflow files
    input_dir_ss = r"..\..\..\MODFLOW\ss"
    mf_name_file_ss = os.path.join(input_dir_ss, "rr_ss.nam")
    mf_ss = flopy.modflow.Modflow.load("rr_ss.nam", "mfnwt", model_ws=os.path.dirname(mf_name_file_ss))

    # read in K zones file
    K_zone = pd.read_csv(K_zone_file, sep=",", header=None)

    # reformat K zones into separate data frames per layer
    num_row = mf_ss.nrow
    K_zone_lay1 = K_zone.iloc[0:num_row]
    K_zone_lay2 = K_zone.iloc[(num_row+1):(num_row+1+num_row)]
    K_zone_lay3 = K_zone.iloc[(num_row+1+num_row+1):(num_row+1+num_row+1+num_row)]

    # create array dict
    array_dict = {"K_zone_1": K_zone_lay1.to_numpy().astype('float64').astype('int32'),
                  "K_zone_2": K_zone_lay2.to_numpy().astype('float64').astype('int32'),
                  "K_zone_3": K_zone_lay3.to_numpy().astype('float64').astype('int32')}

    # set spatial reference info
    xll = 465900
    yll = 4238400
    epsg=26910
    mf_ss.modelgrid.set_coord_info(xoff=xll, yoff=yll, epsg=epsg)

    # create shapefile
    file_name = "K_zones_hru.shp"
    file_path = os.path.join(output_dir_gis, file_name)
    flopy.export.shapefile_utils.write_grid_shapefile(file_path, mf_ss.modelgrid, array_dict, nan_val=-999.98999)



# create shapefile of ponds -------------------------------------------------------------------------------------####

if create_shapefile_of_ponds == 1:
    pass


# create shapefile of all pumping wells (from well package) -----------------------------------------------------####

if create_shapefile_of_wells == 1:
    pass