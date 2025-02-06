import os, sys
import geopandas
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate

Use_Develop_FLOPY = True

if Use_Develop_FLOPY:
    fpth = os.path.abspath(r"D:\Workspace\Codes\flopy_develop\flopy")
    sys.path.insert(0,fpth)
    import flopy
else:
    import flopy

## -----------------------------
# Declaration
## -----------------------------

lake_hru_file = r"D:\Workspace\projects\RussianRiver\Data\gis\hru_lakes.shp"
grid_file = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\gw_proj\grid_info.npy"
bathymetry = r"D:\Workspace\projects\RussianRiver\Data\Lakes\Bathmetery.xls"

lakes = {}

lake_hru = geopandas.read_file(lake_hru_file)
grid_info = np.load(grid_file).all()
grid = grid_info['grid']
mendo_bathy = pd.read_excel(bathymetry, sheet_name='Mendo')
sonoma_bathy = pd.read_excel(bathymetry, sheet_name='Sonoma')

lakes['Menod'] = {"ID":1, 'bathy':mendo_bathy, 'lowest_cell_id':19543} #18531
lakes['Sonoma'] = {"ID":2, 'bathy':sonoma_bathy, 'lowest_cell_id':64373}

mf = flopy.modflow.Modflow('temp.nam')
nlayers = grid.shape[0] - 1
nrows = grid.shape[1]
ncols = grid.shape[2]
dis = flopy.modflow.ModflowDis(mf, nlay=nlayers, nrow= nrows, ncol=ncols,
                               delr=300, delc=300,
                               top= grid[0, :, :], botm=grid[1:, :, :],
                               nper=1, perlen=1, nstp=1,
                               itmuni=4, lenuni=2, xul=0.0,
                               yul=0.0)  # (4) days, 1 ft
thikness = dis.thickness.array
ibound = np.zeros_like(thikness)
ibound[thikness > 0] = 1
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=1)

if True:
    plt.figure()
    modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'column': 63})  # 191
    linecollection = modelxsect.plot_grid()
    modelxsect.plot_ibound()


number_of_intervals = 10
cells_computed = []
distances = []
ElvList = []
if 1:

    for lake in lakes.keys():
        curr_lake = lakes[lake]
        lowest_point = curr_lake['lowest_cell_id']
        low_row = lake_hru[lake_hru.HRU_ID == lowest_point]['HRU_ROW'].values[0]
        low_col = lake_hru[lake_hru.HRU_ID == lowest_point]['HRU_COL'].values[0]

        lake_id = curr_lake['ID']
        curr_lake_hru = lake_hru[lake_hru.LAKE_ID ==  lake_id]
        bathy = curr_lake['bathy']
        bathy['Stage'] = bathy['Stage'] * 0.3048 # from ft to meter
        bathy['Area'] = bathy['Area'] * 4046.86 # from acre to meter2
        bathy['Volume'] = bathy['Volume'] * 1233.48

        min_stage = bathy['Stage'].min() -5.0
        max_stage = bathy['Stage'].max()

        stages = np.linspace(min_stage, max_stage, number_of_intervals)
        f = interpolate.interp1d(bathy['Stage'].values, bathy['Area'].values, fill_value='extrapolate')
        areas = f(stages)
        areas[areas<0] = 0.0
        cumulative_area = 0.0
        for i, stage in enumerate(stages):
            if i == number_of_intervals-1:
                continue

            stage_min = stages[i] + 0.01
            stage_max = stages[i+1] - 0.01
            curr_stage = (stage_min + stage_max)*0.5
            curr_area = areas[i+1] - areas[i]
            #temp_area = np.copy(curr_area)
            #curr_area = curr_area - cumulative_area
            #cumulative_area = cumulative_area + temp_area
            number_of_cells = int(curr_area/(300*300)) + 1
            stages2 = np.linspace(stage_min, stage_max, number_of_cells)

            del_rows = curr_lake_hru['HRU_ROW'].values - low_row
            del_cols = curr_lake_hru['HRU_COL'].values - low_col
            dist_to_min_location =  np.power(np.power(del_cols,2.0) + np.power(del_rows,2.0),0.5)

            # list of cells at this stage
            loc = np.argsort(dist_to_min_location) <= number_of_cells - 1
            curr_lake_hru['distance'] = dist_to_min_location
            curr_lake_hru = curr_lake_hru.sort_values(by=['distance'])

            cell_list = curr_lake_hru[loc]
            cell_list = cell_list.sort_values(by=['distance'])
            index = np.arange(0,len(cell_list))
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
                    distances.append(cell.distance)

                i_row = cell.HRU_ROW - 1
                i_col = cell.HRU_COL - 1
                elevs = grid[:,i_row, i_col]
                for layek, elv in enumerate(elevs):
                    if (elv - curr_stage2) <=0:
                        break;
                elevs[0] = max_stage
                if layek <= 1: # first layer
                    # move layer 2 top to stage, and deactivate layer 1
                    elevs[1] = curr_stage2
                    ibound[0,i_row,i_col] = 0
                    ElvList.append(elevs[1])
                else:
                    # check if lakebed is within 10 meters from the next layer, then move next layer top  up
                    # and make all layers above inactive
                    if curr_stage2 - elevs[layek] <= 10:
                        elevs[layek] = curr_stage2
                        ibound[0:layek, i_row, i_col] = 0
                        ElvList.append( elevs[layek] )
                    else:
                        elevs[layek-1] = curr_stage2
                        ibound[0:layek-1, i_row, i_col] = 0
                        ElvList.append(elevs[layek-1])
                if False:
                    bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=1)
                    plt.figure()
                    modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'row': i_row})  # 191
                    linecollection = modelxsect.plot_grid()
                    modelxsect.plot_ibound()
                pass

dis = flopy.modflow.ModflowDis(mf, nlay=nlayers, nrow= nrows, ncol=ncols,
                               delr=300, delc=300,
                               top= grid[0, :, :], botm=grid[1:, :, :],
                               nper=1, perlen=1, nstp=1,
                               itmuni=4, lenuni=2, xul=0.0,
                               yul=0.0)  # (4) days, 1 ft
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=1)


if True:
    plt.figure()
    modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'column': 63})  # 191
    linecollection = modelxsect.plot_grid()
    modelxsect.plot_ibound()
if True:
    plt.figure()
    #line = [(32935.7,-76116.5),(28927.2,-73923)]
    line = [(33055,-76453),(26590,-73359),(26081, -72712), (25943,-69803)]
    xy = np.array(line)
    modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'line': xy})
    linecollection = modelxsect.plot_grid()
    modelxsect.plot_ibound()
xx = 1