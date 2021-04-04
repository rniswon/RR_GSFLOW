import os, sys
import geopandas
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate

"""
Notes: 
Same as Compute_lake, but was rewritten as a function to be used in the project script.

"""

Use_Develop_FLOPY = True

if Use_Develop_FLOPY:
    fpth = os.path.abspath(r"D:\Workspace\Codes\flopy_develop\flopy")
    sys.path.insert(0, fpth)
    import flopy
else:
    import flopy


def carve_rubber_dam(config, grid, ibound, Lake_array):

    # read in rubber dam lake id
    rubber_dam_lake_id = config.get('SFR', 'rubber_dam_lake_id')
    rubber_dam_lake_id = int(rubber_dam_lake_id)

    # read in rubber dam lake shapefile
    rubber_dam_lake = config.get('LAK', 'rubber_dam_lake')
    rubber_dam_lake = geopandas.read_file(rubber_dam_lake)

    # read in min and max rubber dam lake stages
    min_stage = float(config.get('LAK', 'rubber_dam_min_lake_stage'))
    max_stage = float(config.get('LAK', 'rubber_dam_max_lake_stage'))

    # get row and column indices of rubber dam lake HRUs
    idx_row = rubber_dam_lake.HRU_ROW - 1
    idx_col = rubber_dam_lake.HRU_COL - 1
    elevs = grid[:, idx_row, idx_col]
    ibb = ibound[:, idx_row, idx_col]

    # find top active layer and  determine thickness
    # TODO: figure out what's wrong here
    for k, ib in enumerate(ibb):
        if ib.all() > 0:  # had to add .all() here to avoid getting an error because original code was written for lakes composed of just one grid cell
            break
    top_active_layer = k
    thikness_of_top_active_layer = elevs[top_active_layer] - elevs[top_active_layer + 1]

    # adjust elevations in dis file to account for rubber dam lake
    # TODO: figure out exactly why these changes are made to the elevations and determine whether
    #  they make sense to implement for the rubber dam
    # TODO: consider whether I need to loop through each individual grid cell in the rubber dam in the code
    #  below (and remove all the .all() functions I added) - I think that's necessary
    # TODO: will need to double-check that this makes sense once fix the RR DEM elevations
    for i in range(len(idx_row)):

        if k > 0:
            diff = elevs[k,i] - min_stage
            if diff > 0:
                elevs[k:,i] = elevs[k:,i] - diff
            else:
                if min_stage > elevs[0,i]:
                    elevs[0,i] = max_stage
                    elevs[1,i] = min_stage
                else:
                    elevs[k,i] = elevs[k,i] - diff
        else:
            diff = elevs[k + 1,i] - min_stage
            if diff > 0:
                elevs[k + 1:,i] = elevs[k + 1:,i] - diff
            else:
                if min_stage > elevs[0,i]:
                    elevs[0,i] = max_stage
                    elevs[1,i] = min_stage
                else:
                    elevs[k + 1,i] = elevs[k + 1,i] - diff

    # adjust ibound and lake arrays to account for rubber dam lake
    if top_active_layer == 0:
        ibound[0, idx_row, idx_col] = 0
        Lake_array[0, idx_row, idx_col] = rubber_dam_lake_id
    else:
        ibound[0:top_active_layer, idx_row, idx_col] = 0
        Lake_array[0:top_active_layer, idx_row, idx_col] = rubber_dam_lake_id
    pass
    grid[:, idx_row, idx_col] = elevs




def carve_lakes(gw):
    """

    :param gw: is groundwater object
    :return:
    """
    ## -----------------------------
    # Declaration
    ## -----------------------------
    config = gw.config
    lake_hru_file = config.get('LAK', 'lake_hru_file')
    grid_file = config.get('DIS', 'grid_file')
    bathymetry = config.get('LAK', 'bathymetry_file')
    number_of_intervals = 10

    lakes = {}
    lake_hru = geopandas.read_file(lake_hru_file)
    grid_info = np.load(grid_file, allow_pickle=True).all()
    grid = grid_info['grid']
    mendo_bathy = pd.read_excel(bathymetry, sheet_name='Mendo')
    sonoma_bathy = pd.read_excel(bathymetry, sheet_name='Sonoma')

    lakes['Menod'] = {"ID": 1, 'bathy': mendo_bathy, 'lowest_cell_id': 19543}  # 18531
    lakes['Sonoma'] = {"ID": 2, 'bathy': sonoma_bathy, 'lowest_cell_id': 64373}

    cells_computed = []
    mf = gw.mf
    ibound = mf.bas6.ibound.array
    Lake_array = np.zeros_like(ibound)
    for lake in lakes.keys():
        curr_lake = lakes[lake]
        lowest_point = curr_lake['lowest_cell_id']
        low_row = lake_hru[lake_hru.HRU_ID == lowest_point]['HRU_ROW'].values[0]
        low_col = lake_hru[lake_hru.HRU_ID == lowest_point]['HRU_COL'].values[0]

        lake_id = curr_lake['ID']
        curr_lake_hru = lake_hru[lake_hru.LAKE_ID == lake_id]
        curr_lake_hru = curr_lake_hru.reset_index() # add to remove pandas warning
        bathy = curr_lake['bathy']
        bathy['Stage'] = bathy['Stage'] * 0.3048  # from ft to meter
        bathy['Area'] = bathy['Area'] * 4046.86  # from acre to meter2
        bathy['Volume'] = bathy['Volume'] * 1233.48

        min_stage = bathy['Stage'].min() - 5.0
        max_stage = bathy['Stage'].max()

        stages = np.linspace(min_stage, max_stage, number_of_intervals)
        f = interpolate.interp1d(bathy['Stage'].values, bathy['Area'].values, fill_value='extrapolate')
        areas = f(stages)
        areas[areas < 0] = 0.0
        for i, stage in enumerate(stages):
            if i == number_of_intervals - 1:
                continue

            stage_min = stages[i] + 0.01
            stage_max = stages[i + 1] - 0.01
            curr_stage = (stage_min + stage_max) * 0.5
            curr_area = areas[i + 1] - areas[i]
            number_of_cells = int(curr_area / (300 * 300)) + 1
            stages2 = np.linspace(stage_min, stage_max, number_of_cells)

            del_rows = curr_lake_hru['HRU_ROW'].values - low_row
            del_cols = curr_lake_hru['HRU_COL'].values - low_col
            dist_to_min_location = np.power(np.power(del_cols, 2.0) + np.power(del_rows, 2.0), 0.5)

            # list of cells at this stage
            loc = np.argsort(dist_to_min_location) <= number_of_cells - 1
            curr_lake_hru['distance'] = dist_to_min_location
            curr_lake_hru = curr_lake_hru.sort_values(by=['distance'])

            cell_list = curr_lake_hru[loc]
            cell_list = cell_list.sort_values(by=['distance'])
            index = np.arange(0, len(cell_list))
            cell_list = cell_list.set_index(index)

            not_loc = np.logical_not(loc)
            curr_lake_hru = curr_lake_hru[not_loc]

            # find the layer where the stage exists
            for j, cell in cell_list.iterrows():
                curr_stage2 = stages2[j]
                i_id = cell.HRU_ID
                if i_id in cells_computed:
                    continue
                else:
                    cells_computed.append(i_id)

                i_row = cell.HRU_ROW - 1
                i_col = cell.HRU_COL - 1
                elevs = grid[:, i_row, i_col]
                for layek, elv in enumerate(elevs):
                    if (elv - curr_stage2) <= 0:
                        break;
                elevs[0] = max_stage
                if layek <= 1:  # first layer
                    # move layer 2 top to stage, and deactivate layer 1
                    elevs[1] = curr_stage2
                    ibound[0, i_row, i_col] = 0
                    Lake_array[0, i_row, i_col] = lake_id

                else:
                    # check if lakebed is within 10 meters from the next layer, then move next layer top  up
                    # and make all layers above inactive
                    if curr_stage2 - elevs[layek] <= 10:
                        elevs[layek] = curr_stage2
                        ibound[0:layek, i_row, i_col] = 0
                        Lake_array[0:layek, i_row, i_col] = lake_id

                    else:
                        elevs[layek - 1] = curr_stage2
                        ibound[0:layek - 1, i_row, i_col] = 0
                        Lake_array[0:layek - 1, i_row, i_col] = lake_id

                grid[:, i_row, i_col] = elevs


        # just for debuging the lake cross sections
    if False:
        gw.mf.dis.top = grid[0, :, :]
        gw.mf.dis.botm = grid[1:, :, :]
        gw.mf.bas6.ibound = ibound
        plt.figure()
        modelxsect = flopy.plot.ModelCrossSection(model=gw.mf, line={'column': 63})  # 191
        linecollection = modelxsect.plot_grid()
        modelxsect.plot_ibound()

    # get small reservoirs
    stage_range = pd.read_excel(bathymetry, sheet_name='Stage_range')
    for lake_id in range(3,12):
        curr_lake_hru = lake_hru[lake_hru['LAKE_ID'] == lake_id]
        i_row = curr_lake_hru.HRU_ROW - 1
        i_col = curr_lake_hru.HRU_COL - 1
        elevs = grid[:, i_row, i_col]
        ibb = ibound[:,i_row, i_col]

        for k, ib in enumerate(ibb):
            if ib >0:
                break
        top_active_layer = k
        thikness_of_top_active_layer = elevs[top_active_layer] - elevs[top_active_layer+1]
        stage_up = stage_range[stage_range['Lake _ID'] == lake_id]['Stage up'].values[0]
        stage_dn = stage_range[stage_range['Lake _ID'] == lake_id]['Down'].values[0]

        #
        if k > 0:
            diff = elevs[k] - stage_dn
            if diff > 0:
                elevs[k:] = elevs[k:] - diff
            else:
                if stage_dn > elevs[0]:
                    elevs[0] = stage_up
                    elevs[1] = stage_dn
                else:
                    elevs[k] = elevs[k] - diff
        else:
            diff = elevs[k+1] - stage_dn
            if diff > 0:
                elevs[k+1:] = elevs[k+1:] - diff
            else:
                if stage_dn > elevs[0]:
                    elevs[0] = stage_up
                    elevs[1] = stage_dn
                else:
                    elevs[k+1] = elevs[k+1] - diff




        # if (stage_up - stage_dn) <= 0.5*thikness_of_top_active_layer:
        #     low_dist = stage_up - stage_dn
        # else:
        #     low_dist =  0.5*thikness_of_top_active_layer
        # drop = elevs[top_active_layer] - low_dist
        # elevs[top_active_layer] = drop

        if top_active_layer == 0:
            ibound[0, i_row, i_col] = 0
            Lake_array[0, i_row, i_col] = lake_id
        else:
            ibound[0:top_active_layer, i_row, i_col]=0
            Lake_array[0:top_active_layer, i_row, i_col] = lake_id
        pass
        grid[:,i_row, i_col] = elevs

    # make changes for the rubber dam
    carve_rubber_dam(config, grid, ibound, Lake_array)

    # update model dis and bas
    gw.mf.dis.top = grid[0, :, :]
    gw.mf.dis.botm = grid[1:, :, :]
    gw.mf.bas6.ibound = ibound
    gw.mfs.dis.top = grid[0, :, :]
    gw.mfs.dis.botm = grid[1:, :, :]
    gw.mfs.bas6.ibound = ibound
    gw.Lake_array = Lake_array