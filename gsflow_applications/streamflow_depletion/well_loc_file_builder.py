import os
import numpy as np
import pandas as pd
import flopy

#mm = flopy.modflow.Modflow(version='mfnwt')
#wel = flopy.modflow.ModflowWel.load('./modflow/input/pumping_with_rural.wel', mm)

newlin = '\n'
thisFolder = os.getcwd()
root = os.path.sep.join(thisFolder.split(os.path.sep)[:-1])
# get the wells in the archive model from the following file
# the wells in the updated model are in this file
upwellFile = open('./modflow/input/rural_pumping.wel', 'r')
# create the following file with select wells from the archive model inserted
# outwellFile.write('run_id,lay,row,col,tlay,blay,nlay{}'.format(newlin))
line = upwellFile.readline()  # text
line = upwellFile.readline()  # options
line = upwellFile.readline()  # specify phiramp
line = upwellFile.readline()  # end
line = upwellFile.readline()  # max well num
line = upwellFile.readline()  # sp 1 header
a = line.split()
nwel = int(a[0])
# build a dataframe with rows and columns
ar_lay = np.array([], dtype=int)
ar_row = np.array([], dtype=int)
ar_col = np.array([], dtype=int)
ar_mfrowcol = np.array([], dtype=str)
for w in range(nwel):
    line = upwellFile.readline()
    a = line.split()
    ar_lay = np.append(ar_lay, int(a[0])-1)
    ar_row = np.append(ar_row, int(a[1])-1)
    ar_col = np.append(ar_col, int(a[2])-1)
    ar_mfrowcol = np.append(ar_mfrowcol, 'c{}{}'.format(a[1].zfill(3), a[2].zfill(3)))
upwellFile.close()
df = pd.DataFrame()
df['lay'] = ar_lay
df['row'] = ar_row
df['col'] = ar_col
df['mfrowcol'] = ar_mfrowcol
df_min = df.groupby(by=['mfrowcol']).min(['layer'])
df_max = df.groupby(by=['mfrowcol']).max(['layer'])
df_merge = df_min.merge(df_max, left_index=True, right_index=True, suffixes=['_min', '_max'])
df_merge['nlay'] = df_merge['lay_max'] - df_merge['lay_min'] + 1
ar_run_id = np.arange(0, df_merge['lay_min'].count(), dtype=int)
df_merge['run_id'] = ar_run_id
ulx = 466050
uly = 4361550
cellsize = 312
df_merge['xcoord'] = (df_merge['col_min'] - 1) * cellsize + ulx
df_merge['ycoord'] = uly - (df_merge['row_min'] - 1) * cellsize
df_merge.to_csv('./windows/well_locations.csv', index_label='mfrowcol', index=True,
                columns=['run_id', 'lay_min', 'lay_max', 'nlay','row_min', 'col_min', 'xcoord','ycoord'],
                header=['run_id', 'tlay', 'blay', 'nlay', 'row', 'col', 'xcoord', 'ycoord'])
print('done.')
