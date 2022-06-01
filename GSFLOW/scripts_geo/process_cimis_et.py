import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import geopandas
import geopandas
import rasterio
from rasterio.plot import show



# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set mean monthly sim PRMS ET file
prms_pet_monthly_file = os.path.join(repo_ws, "MODFLOW", "init_files", "gsflow_sim_nhru_potet_meanmonthly.csv")

# set CIMIS ET folder
cimis_et_folder = os.path.join(repo_ws, "..", "..", "data", "gis", "ETo_spatial_maps")

# set CIMIS ET folder for output monthly mean by year csvs
cimis_et_monthly_mean_by_year_folder = os.path.join(repo_ws, "..", "..", "data", "gis", "ETo_spatial_maps", "monthly_mean", "by_year")

# set CIMIS ET folder for output monthly mean over all years csv
cimis_et_monthly_mean_folder = os.path.join(repo_ws, "..", "..", "data", "gis", "ETo_spatial_maps", "monthly_mean")

# set file for monthly mean reference ET output
ref_et_monthly_mean_file = os.path.join(cimis_et_monthly_mean_folder, 'et_monthly_mean_all_years.csv')

# set hru points file
hru_points_file = os.path.join(repo_ws, "..", "..", "data", "gis", "Model_grid", "hru_params_points.shp")

# set ag data file
ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")

# set ag data file, updated with ET data
ag_dataset_et_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_et.csv")

# set crop coefficient file
kc_file = os.path.join(repo_ws, "MODFLOW", "init_files", "KC_sonoma_shared_kc_info.csv")

# set pet ratio calc error file
pet_ratio_calc_error_file = os.path.join(script_ws, "outputs", "pet_ratio_calc_error_file.csv")

# set pet ratio calc error file
pet_ratio_by_hru_file = os.path.join(script_ws, "outputs", "pet_ratio_by_hru.csv")


# set min and max start and end dates for CIMIS ET data processing
min_start_year = 1990
max_end_year = 2015

# script settings
extract_cimis_data = 1
calculate_monthly_mean_prms_pet = 0
calculate_pet_ratio_for_ag_fields = 0
calculate_pet_ratio_for_ag_hrus = 0



# ---- Extract CIMIS data -------------------------------------------####

if extract_cimis_data == 1:

    # ---- Read in points in RR watershed -------------------------------------------####

    # read in hru points file and reproject to CIMIS projection
    hru_points = geopandas.read_file(hru_points_file)

    # select desired columns and rows
    hru_points = hru_points[['HRU_ID', 'HRU_TYPE', 'HRU_ROW', 'HRU_COL', 'HRU_X', 'HRU_Y', 'HRU_LAT', 'HRU_LON', 'geometry']]
    hru_points = hru_points[hru_points['HRU_TYPE'] > 0]

    # reproject
    hru_points_reproj = hru_points.to_crs('EPSG: 3310')



    # ---- Read in CIMIS data and extract ET -------------------------------------------####

    # get file names for CIMIS ET files
    et_files = [x for x in os.listdir(cimis_et_folder) if x.endswith('.tif')]

    # loop through CIMIS ET files
    et_hru_list = []
    for et_file in et_files:

        # extract data start and end dates
        file_name = et_file
        tmp = file_name.split('.')
        tmp = tmp[0].split('_')
        tmp = tmp[1].split('-')
        start_date_year = tmp[0][0:4]
        start_date_month = tmp[0][4:6]
        start_date_day = tmp[0][6:9]
        start_date = start_date_year + '-' + start_date_month + '-' + start_date_day
        end_date_year = tmp[1][0:4]
        end_date_month = tmp[1][4:6]
        end_date_day = tmp[1][6:9]
        end_date = end_date_year + '-' + end_date_month + '-' + end_date_day

        if (int(start_date_year) >= min_start_year) & (int(end_date_year) <= max_end_year):

            # print
            print("Processing " + et_file)

            # create hru df to extract CIMIS ET data to
            hru_df = hru_points_reproj.copy()
            hru_df.reset_index(drop=True, inplace=True)

            # read in
            et_file = os.path.join(cimis_et_folder, et_file)
            et = rasterio.open(et_file)

            # # plot to check that it is reprojected correctly
            # fig, ax = plt.subplots()
            # extent = [et.bounds[0], et.bounds[2], et.bounds[1],
            #           et.bounds[3]]  # transform rasterio plot to real world coords
            # ax = rasterio.plot.show(et, extent=extent, ax=ax, cmap='pink')
            # hru_df.plot(ax=ax)

            # sample the CIMIS ET at the points
            coord_list = [(x,y) for x,y in zip(hru_df['geometry'].x , hru_df['geometry'].y)]
            hru_df['value'] = [x for x in et.sample(coord_list)]

            # place ET data in a separate column per day
            et_df = pd.DataFrame(hru_df['value'].values.tolist())
            et_df.columns = pd.date_range(start=start_date, end=end_date)
            id_vars = ['HRU_ID', 'HRU_TYPE', 'HRU_ROW', 'HRU_COL', 'HRU_X', 'HRU_Y', 'HRU_LAT', 'HRU_LON']
            et_df = pd.concat([hru_df[id_vars], et_df], axis=1)

            # convert et_df to long format
            et_df = pd.melt(et_df, id_vars=id_vars, var_name='date', value_name = 'et')

            # add month column
            et_df['month'] = et_df['date'].dt.month

            # calculate monthly mean ET values for each hru
            id_vars_month = id_vars + ['month']
            et_monthly_mean = et_df.groupby(id_vars_month, as_index=False)['et'].mean()

            # add year column
            et_monthly_mean['year'] = start_date_year

            # export
            file_name = "et_monthly_mean_" + start_date_year + '.csv'
            file_path = os.path.join(cimis_et_monthly_mean_by_year_folder, file_name)
            et_monthly_mean.to_csv(file_path, index=False)


    # ---- Calculate monthly mean ET values over all years -------------------------------------------####

    # get file names for monthly mean CIMIS ET files
    et_monthly_mean_files = [x for x in os.listdir(cimis_et_monthly_mean_by_year_folder) if x.endswith('.csv')]

    # loop over files and read in ET monthly mean
    et_list = []
    for et_file in et_monthly_mean_files:

        # read in monthly mean ref ET file
        et_file = os.path.join(cimis_et_monthly_mean_by_year_folder, et_file)
        ref_et = pd.read_csv(et_file)

        # store
        et_list.append(ref_et)

    # combine into one data frame
    et_df = pd.concat(et_list, axis=0, ignore_index=True)

    # calculate monthly mean ET values over all years for each HRU
    id_vars = ['HRU_ID', 'HRU_TYPE', 'HRU_ROW', 'HRU_COL', 'HRU_X', 'HRU_Y', 'HRU_LAT', 'HRU_LON', 'month']
    et_df_monthly_mean = et_df.groupby(id_vars, as_index=False)['et'].mean()

    # export
    et_df_monthly_mean.to_csv(ref_et_monthly_mean_file, index=False)




# ---- Calculate monthly mean PRMS PET for each HRU ----------------------------------------------####

if calculate_monthly_mean_prms_pet == 1:

    # read in PRMS PET data
    pet_prms = pd.read_csv(prms_pet_monthly_file)

    # convert to long format
    pet_prms = pd.melt(pet_prms, id_vars='Date', var_name='hru', value_name='pet_prms')

    # add month column
    pet_prms['Date'] = pd.to_datetime(pet_prms['Date'])
    pet_prms['month'] = pet_prms['Date'].dt.month

    # group by month and hru, then take mean
    pet_prms = pet_prms.groupby(['hru', 'month'], as_index=False)['pet_prms'].mean()
    pet_prms['hru'] = pd.to_numeric(pet_prms['hru'])

    # convert units (from inches to mm)
    inches_to_mm = 25.4
    pet_prms['pet_prms'] = pet_prms['pet_prms'] * inches_to_mm




# ---- Calculate PET ratio for each ag field, month combo ----------------------------------------------####

if calculate_pet_ratio_for_ag_fields == 1:

    # read in ag data
    ag_data = pd.read_csv(ag_dataset_file)

    # read in monthly mean reference ET data
    et_ref = pd.read_csv(ref_et_monthly_mean_file)

    # read in crop coefficient data
    kc_data = pd.read_csv(kc_file)


    # add columns to ag data
    months = list(range(1,13))
    for month in months:

        # create column names
        kc_col = 'kc_' + str(month)   # NOTE: in months when crop is not irrigated, set kc to 1 in kc_col
        pet_prms_col = 'pet_prms_' + str(month)
        et_ref_col = 'et_ref_' + str(month)
        ratio_col = 'ratio_' + str(month)

        # create columns
        ag_data[kc_col] = np.nan
        ag_data[pet_prms_col] = np.nan
        ag_data[et_ref_col] = np.nan
        ag_data[ratio_col] = np.nan


    # loop through hrus with ag fields
    field_hrus = ag_data['field_hru_id'].unique()
    num_field_hrus = len(field_hrus)
    error_df_colnames = ['field_hru', 'field_id', 'month']
    error_df = pd.DataFrame(columns = error_df_colnames)
    i=0
    for field_hru in field_hrus:

        # print
        i=i+1
        print("Processing AG HRU " + str(field_hru) + ': ',  str(i) + ' of ' + str(num_field_hrus))

        # get field ids in this hru
        mask_field_hru = ag_data['field_hru_id'] == field_hru
        field_ids = ag_data.loc[mask_field_hru, 'field_id'].values

        # loop through fields in this hru
        for field_id in field_ids:

            # get field mask in ag_data
            mask_ag_data = (ag_data['field_hru_id'] == field_hru) & (ag_data['field_id'] == field_id)

            # get crop type for this field
            crop = ag_data.loc[mask_ag_data, 'crop_type'].values[0]

            # loop through months
            for month in months:

                # get column names in ag_data
                kc_col = 'kc_' + str(month)  # NOTE: in months when crop is not irrigated, set kc to 1 in kc_col
                pet_prms_col = 'pet_prms_' + str(month)
                et_ref_col = 'et_ref_' + str(month)
                ratio_col = 'ratio_' + str(month)

                try:

                    # get kc data for this field
                    kc_mask = kc_data['CropName2'] == crop
                    kc_data_col_kc = 'KC_' + str(month)
                    kc_data_col_notirrig = 'NotIrrigated_' + str(month)
                    kc_val = kc_data.loc[kc_mask, kc_data_col_kc].values[0]
                    not_irrig_val = kc_data.loc[kc_mask, kc_data_col_notirrig].values[0]
                    if not_irrig_val == 1:  # assuming that Not_Irrigated columns indicate that the crop is not irrigated when the value is 1 and is irrigated when the value is 0
                        kc_val = 1
                    ag_data.loc[mask_ag_data, kc_col] = kc_val

                    # get prms pet data for this field
                    pet_prms_mask = (pet_prms['hru'] == field_hru) & (pet_prms['month'] == month)
                    pet_val = pet_prms.loc[pet_prms_mask, 'pet_prms'].values[0]
                    ag_data.loc[mask_ag_data, pet_prms_col] = pet_val

                    # get ref et data for this field
                    et_ref_mask = (et_ref['HRU_ID'] == field_hru) & (et_ref['month'] == month)
                    et_ref_val = et_ref.loc[et_ref_mask, 'et'].values[0]
                    ag_data.loc[mask_ag_data, et_ref_col] = et_ref_val

                    # calculate ratio for this field
                    ratio_val = (kc_val * et_ref_val)/pet_val
                    if not_irrig_val == 1:   # if field not irrigated during this months, set the ratio to 1
                        ratio_val = 1
                    ag_data.loc[mask_ag_data, ratio_col] = ratio_val

                except:

                    # handle error
                    print("Error for: AG HRU " + str(field_hru) + ", AG field id ", str(field_id) + ", month " + str(month))
                    this_error_df = pd.DataFrame({'field_hru': [field_hru], 'field_id': [field_id], 'month': [month]})
                    error_df = error_df.append(this_error_df)

                    # set ratio val
                    ratio_val = 1
                    ag_data.loc[mask_ag_data, ratio_col] = ratio_val


    # export
    ag_data.to_csv(ag_dataset_et_file, index=False)
    error_df.to_csv(pet_ratio_calc_error_file, index=False)




# ---- Calculate ET ratio for each ag HRU, month combo ----------------------------------------------####

if calculate_pet_ratio_for_ag_hrus == 1:

    # read in ag_dataset_et_file
    ag_data = pd.read_csv(ag_dataset_et_file)

    # create data frame with column of unique ag HRUs and 12 ET ratio columns (one per month)
    field_hrus = ag_data['field_hru_id'].astype(int).unique()
    et_ratio_df = pd.DataFrame({'hru_id': field_hrus, 'ratio_1': np.nan, 'ratio_2': np.nan, 'ratio_3': np.nan, 'ratio_4': np.nan, 'ratio_5': np.nan,
                                'ratio_6': np.nan, 'ratio_7': np.nan, 'ratio_8': np.nan, 'ratio_9': np.nan, 'ratio_10': np.nan, 'ratio_11': np.nan,
                                'ratio_12': np.nan})

    # loop through ag HRUs
    for field_hru in field_hrus:

        # create a subset df for this ag HRU
        df = ag_data[ag_data['field_hru_id'] == field_hru]

        # calculate sum of all field fac (i.e. ag frac) values to get ag_frac_sum and non_ag_frac
        ag_frac_sum = df['field_fac'].sum()
        non_ag_frac = 1-ag_frac_sum

        # loop through months
        months = list(range(1, 13))
        for month in months:

            # get ratio column name for this month
            ratio_col = 'ratio_' + str(month)

            # apply equation in notebook to calculate ratio for this HRU and month
            ratio_non_ag = 1
            ratio_hru = sum(df['field_fac'] * df[ratio_col]) + (non_ag_frac * ratio_non_ag)

            # store hru ratio in et_ratio_df
            mask = et_ratio_df['hru_id'] == field_hru
            et_ratio_df.loc[mask, ratio_col] = ratio_hru

    # export
    et_ratio_df.to_csv(pet_ratio_by_hru_file, index=False)
