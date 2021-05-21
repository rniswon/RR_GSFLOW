import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

Use_Develop_FLOPY = True

if Use_Develop_FLOPY:
    fpth = sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy")
    sys.path.append(fpth)
    import flopy
else:
    import flopy
# import h5py as h5
import configparser
import geopandas
from calendar import monthrange
# import includes
from scipy import interpolate
import support


class Gw_model(object):
    def __init__(self, config):
        self.config = config
        self.work_space = config.get('General_info', 'work_space')
        self.ss_model_name = config.get('General_info', 'steady_state_name')
        self.tr_model_name = config.get('General_info', 'tran_name')

        # init modflow object
        self.model_init()

        # load hru_param binary file
        print("Loading HRU files....")
        self.hru_param_file = self.config.get('DIS', 'hru_shp')
        self.hru_param = geopandas.read_file(self.hru_param_file)
        self.hru_param = self.hru_param.sort_values(by=['HRU_ID'])

    def model_init(self):
        """
        :return:
        """
        mdfexe = self.config.get('General_info', 'modflow_exe')
        ws = os.path.join(self.work_space, "tr")
        self.mf = flopy.modflow.Modflow(self.tr_model_name, exe_name=mdfexe,
                                        model_ws=ws, version='mfnwt')

        # steady state folder
        ws = os.path.join(self.work_space, "ss")
        self.mfs = flopy.modflow.Modflow(self.ss_model_name, exe_name=mdfexe,
                                         model_ws=ws, version='mfnwt')

    def dis_package(self):
        """

        :return:
        """

        print("Working on generating the dis object .... ")

        ###-------------------------------
        self.nrows = self.hru_param["HRU_ROW"].max()
        self.ncols = self.hru_param["HRU_COL"].max()
        self.nlayers = int(self.config.get('DIS', 'nlayers'))
        del_r = self.hru_param.HRU_X[1] - self.hru_param.HRU_X[0]
        del_c = del_r

        print("Compute grid geometry ...")
        # load geological dataframe
        self.geo_df = geopandas.read_file(self.config.get('Geo_Framework', 'filename'))
        self.geo_df = self.geo_df.sort_values(by=['HRU_ID'])
        support.compute_grid_geometry(self)

        # Read excel file for stress periods
        xfile = self.config.get('Budget_info', 'budget_excel_file')
        self.time_df = support.read_time_dis_file(xfile, sheet='time_dis')
        self.perlen = self.time_df['days'].values
        self.nper = len(self.perlen)
        self.nstp = np.copy(self.perlen)
        self.SteadyID = np.zeros_like(self.perlen, dtype=np.bool)

        # TODO : Add coordinate
        # transient
        dis = flopy.modflow.ModflowDis(self.mf, nlay=self.nlayers, nrow=self.nrows, ncol=self.ncols,
                                       delr=del_r, delc=del_c,
                                       top=self.grid_3d[0, :, :], botm=self.grid_3d[1:, :, :],
                                       nper=self.nper, perlen=self.perlen, nstp=self.nstp, steady=self.SteadyID,
                                       itmuni=4, lenuni=2, xul=0.0,
                                       yul=0.0)  # (4) days, 2 meter

        # steady state
        diss = flopy.modflow.ModflowDis(self.mfs, nlay=self.nlayers, nrow=self.nrows, ncol=self.ncols,
                                        delr=del_r, delc=del_c,
                                        top=self.grid_3d[0, :, :], botm=self.grid_3d[1:, :, :],
                                        nper=1, perlen=1, nstp=1, steady=True,
                                        itmuni=4, lenuni=2, xul=0.0,
                                        yul=0.0)  # (4) days, 1 ft

        print(" Done generating dis object .....")

    def bas_package(self, wt):
        """

        :param wt:
        :return:
        """
        if not (wt is None):
            strt = wt
        else:
            # no wt is used, then the initial wt will close to surface
            strt = self.mf.dis.top.array - 0.0

        thikness = self.mf.dis.thickness.array
        ibound = np.zeros_like(thikness)
        ibound[thikness > 0] = 1

        # find hru_type = 1 but thickness is zero
        hru_type = self.hru_param['HRU_TYPE'].values
        hru_type = hru_type.reshape(self.nrows, self.ncols)
        tot_thick = thikness.sum(axis=0)
        mask = np.logical_and(tot_thick > 0, hru_type == 0)
        for k in range(ibound.shape[0]):
            var_ = ibound[k, :, :].copy()
            var_[mask] = 0
            ibound[k, :, :] = var_

        bas = flopy.modflow.ModflowBas(self.mf, ibound=ibound, strt=strt)
        bass = flopy.modflow.ModflowBas(self.mfs, ibound=ibound, strt=strt)
        print("Done generating bas object ....")

    def add_rubber_dam_bas(self, ibound):

        # read in rubber dam lake shapefile
        rubber_dam_lake = self.config.get('RUBBER_DAM', 'rubber_dam_lake')
        rubber_dam_lake = geopandas.read_file(rubber_dam_lake)

        # get HRU row and column of rubber dam lake cells
        hru_row = rubber_dam_lake["HRU_ROW"]
        hru_col = rubber_dam_lake["HRU_COL"]

        # set IBOUND = 0 in layer 1 for rubber dam lake cells
        # TODO: double check that ibound should be indexed in this order: layer, row, column
        # TODO: check that this is changing the values in the correct grid cells
        for i in range(len(hru_row)):
            ibound[0, hru_row[i] - 1, hru_col[
                i] - 1] = 0  # NOTE: have to subtract one to get 0-based indices of these rows and columns in ibound array

        return ibound

    def bas_package_01(self, wt):
        """

        :param wt:
        :return:
        """

        # ---- Set starting heads ------------------------------------------------------------------------
        if not (wt is None):
            strt = wt
        else:
            # no wt is used, then the initial wt will close to surface
            strt = self.mf.dis.top.array - 0.0

        # ---- Create ibound array ------------------------------------------------------------------------
        thikness = self.mf.dis.thickness.array
        ibound = np.zeros_like(thikness)
        ibound[thikness > 0] = 1

        # ---- Make sure that all active cells have non-zero thickness ----------------------------------
        # find hru_type = 1 but thickness is zero
        hru_type = self.hru_param['HRU_TYPE'].values
        hru_type = hru_type.reshape(self.nrows, self.ncols)
        tot_thick = thikness.sum(axis=0)
        mask = np.logical_and(tot_thick > 0, hru_type == 0)
        for k in range(ibound.shape[0]):
            var_ = ibound[k, :, :].copy()
            var_[mask] = 0
            ibound[k, :, :] = var_

        # ---- Incorporate rubber dam ------------------------------------------------------------------
        ibound = self.add_rubber_dam_bas(ibound)

        # ---- Write transient and steady state BAS packages ------------------------------------------
        bas = flopy.modflow.ModflowBas(self.mf, ibound=ibound, strt=strt)
        bass = flopy.modflow.ModflowBas(self.mfs, ibound=ibound, strt=strt)
        print("Done generating bas object ....")

    def upw_package(self, geo_zones):
        """

        :param geo_zones:
        :return:
        """
        if len(geo_zones) > 0:
            pass
        else:
            # use defualt values
            ss = 1e-05
            sy = 0.18
            hk = 1e-3 + np.zeros_like(self.Zone3D, dtype=float)

            hk[self.Zone3D == 14] = 1.0e-4  # bedrock
            hk[self.Zone3D == 15] = 0.001  # sonoma volcanics
            hk[self.Zone3D == 16] = 0.5  # Consolidated Sediments
            hk[self.Zone3D == 17] = 1.0  # Unconsolidated Sediments
            hk[self.Zone3D == 18] = 3.0  # Channel Deposits
            hk[self.Zone3D == 19] = 3.0  # Channel Deposits
        # vka = hk * 0.1
        laytyp = np.ones(self.nlayers)  # convertable layer
        laywet = np.zeros(self.nlayers)

        # Rich suggested increase hk by 2 for the first two layers
        hk[0, :, :] = hk[0, :, :] * 2.0
        hk[1, :, :] = hk[1, :, :] * 2.0

        upw = flopy.modflow.mfupw.ModflowUpw(self.mf, laytyp=laytyp, layavg=0, chani=1.0, layvka=0, laywet=laywet,
                                             hdry=-1e+30, iphdry=0, hk=hk, hani=1.0, vka=hk, ss=ss,
                                             sy=sy, vkcb=0.0, noparcheck=False, ipakcb=55)
        # add package to steady state
        upws = flopy.modflow.mfupw.ModflowUpw(self.mfs, laytyp=laytyp, layavg=0, chani=1.0, layvka=0, laywet=laywet,
                                              hdry=-1e+30, iphdry=0, hk=hk, hani=1.0, vka=hk, vkcb=0.0,
                                              noparcheck=False, ipakcb=55)
        pass

    def remove_field_num(self, a, i):
        names = list(a.dtype.names)
        new_names = names[:i] + names[i + 1:]
        try:
            b = a[new_names]
        except:
            pass
        return b

    def compute_stream_widths(self):
        att_table = self.hru_param

        flo_acc = self.hru_param.DEM_FLOWAC.values
        max_wdith = 40.0
        min_width = 7.0
        width_range = max_wdith - min_width

        widths = min_width + width_range * (flo_acc - min(flo_acc)) / (max(flo_acc) - min(flo_acc))

        streem_info_loc = att_table['ISEG'] > 0
        nss = np.max(att_table['ISEG'].values)
        stream_widths = []
        for seg_id in np.arange(1, nss + 1):
            loc = att_table['ISEG'].values == seg_id
            up = max(widths[loc])
            dn = min(widths[loc])
            stream_widths.append([seg_id, up, dn])
        self.stream_widths = np.array(stream_widths)

    def sfr2_package(self):

        from flopy.utils.optionblock import OptionBlock

        options = OptionBlock('', flopy.modflow.ModflowSfr2, block=True)
        options.reachinput = True  # False
        options.tabfiles = True

        # read flow accumulation file
        flo_acc = self.config.get('SFR', 'str_flow_acc')
        sfr_with_floacc = geopandas.read_file(flo_acc)  #
        sfr_with_floacc = sfr_with_floacc.sort_values(by='HRU_ID')

        hru_shp = self.hru_param
        mask = hru_shp['ISEG'] > 0
        streams_data = hru_shp[mask]  # a compact form is streams_data = hru_shp[hru_shp['ISEG'] > 0]
        streams_data = streams_data.sort_values(by='HRU_ID')
        streams_data['flow_accum'] = sfr_with_floacc['grid_code'].values

        ## Reach Data
        # The reach data will be saved in a Pandas dataframe, which will make it simpler to handle the tabular data.
        # Table fields name
        reach_data_labels = ['node', 'k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope',
                             'strthick', 'strhc1', 'thts', 'thti', 'eps', 'uhc', 'reachID', 'outreach']

        # Initialize an empty pandas dataframe
        reach_data = pd.DataFrame(columns=reach_data_labels, dtype='float')

        # Reach location
        reach_data['k'] = 0  # layer number-- Notice that layer numbers are zero-based
        reach_data['i'] = streams_data['HRU_ROW'].values - 1  # row number
        reach_data['j'] = streams_data['HRU_COL'].values - 1  # column number

        for index, rech in reach_data.iterrows():  # get layer
            thk = self.mf.dis.thickness.array[:, int(rech['i']), int(rech['j'])]
            if sum(thk) == 0:
                raise ValueError("Stream in inactive zone")
            for kk, val in enumerate(thk):
                if val > 0:
                    # reach_data.set_value(index, 'k', kk)
                    reach_data.at[index, 'k'] = kk
                    break
            pass

        # IDs
        reach_data['iseg'] = streams_data['ISEG'].values  # Segment ID number
        reach_data['ireach'] = streams_data['IREACH'].values  # Reach ID number
        # reach_data['ireach'][reach_data['ireach'] < 1] = 1
        reach_data.loc[reach_data['ireach'] < 1, 'ireach'] = 1  # the newly added segments (div and spillways) has
        # ireach =0

        # Stream topography
        reach_data['rchlen'] = streams_data['RCHLEN'].values  # reach length
        reach_data.loc[reach_data['rchlen'] == 0, 'rchlen'] = 300.0
        reach_data['strtop'] = streams_data[
                                   'DEM_ADJ'].values - 1.0  # Streambed elevation is assumed 1 meter below ground surface.
        reach_data['slope'] = streams_data['DEM_SLP_P'].values  # / 100.0  # Slope #todo: divid by 100 is not correct!!

        # Streambed information
        reach_data['strthick'] = 0.5  # streambed thickness - meter
        reach_data['strhc1'] = 0.1  # conductivity of the stream bed

        # Unsaturated Zone properties
        reach_data['thts'] = 0.31  # saturated porosity
        reach_data['thti'] = 0.131  # initial water content
        reach_data['eps'] = 3.5  # Brooks-Corey exponent
        reach_data['uhc'] = 0.1  # conductivity of the unsaturated zone
        n_reaches = len(reach_data)  # number of reaches

        reach_data = self.calculate_stream_slope(reach_data)

        seg_data_labels = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior',
                           'nstrpts', 'flow', 'runoff', 'etsw', 'pptsw', 'roughch', 'roughbk',
                           'cdpth', 'fdpth', 'awdth', 'bwdth', 'hcond1', 'thickm1',
                           'elevup', 'width1', 'depth1', 'hcond2', 'thickm2', 'elevdn',
                           'width2', 'depth2']

        # compute width based on flow accumulation
        streams_data = self.cal_stream_width(streams_data, flo_acc)

        # Use the stream data from the HRU shapefile
        unique_segments = streams_data.drop_duplicates(['ISEG'], keep='first')
        unique_segments = unique_segments.sort_values(by='ISEG')

        n_segments = len(unique_segments)

        # initialize segments dataframe filled with zeros
        zero_data = np.zeros((n_segments, len(seg_data_labels)))
        segment_data = pd.DataFrame(zero_data, columns=seg_data_labels, dtype='float')

        # fill in segments data frame
        segment_data['nseg'] = unique_segments['ISEG'].values  # Segment ID
        segment_data['icalc'] = 1  # Use Manning's Equation for a rectangular cross-section
        segment_data['outseg'] = unique_segments['OUTSEG'].values  # Downstream Segment
        segment_data['iupseg'] = unique_segments[
            'IUPSEG'].values  # segmet id for Upstream diversion or negative ID of the lake
        segment_data['width1'] = unique_segments['Width'].values  # Upstream width
        segment_data['width2'] = unique_segments['Width'].values  # Downstream width
        segment_data['roughch'] = float(self.config.get('SFR', 'mannings_roughness'))
        ## This the options in the first line in the SFR package
        nsfrpar = 0  # number of parameters
        nparseg = 0
        isfropt = 3  # uzf is simulated, k is read from uzf
        const = 86400  # constant for manning's equation, units of ??
        dleak = 0.0001  # closure tolerance for stream stage computation
        ipakcb = 55  # flag for writing SFR output to cell-by-cell budget (on unit 55)
        istcb2 = 81  # flag for writing SFR output to text file
        nstrail = 15  # used when USZ is simulated, number of trailing wave increments
        isuzn = 1  # used when USZ is simulated, number of vertical cells in unz, for icalc=1, isuzn = 1
        nsfrsets = 50  # used when USZ is simulated, number of sets of trailing wave
        irtflg = 0  # an integer value that flags whether transient streamflow routing is active
        numtim = 2  # used when irtflg > 0, number of sub time steps to route streamflow
        weight = 0.75  # used when irtflg > 0,A real number equal to the time weighting factor used to calculate the change in channel storage.

        if True:
            # todo: from now on we must slice hru_df and assign to reach_data
            reach_data = reach_data.reset_index()
            del (reach_data['index'])
            reach_data, segment_data = self.add_ag_full_diversions_segs(segment_data=segment_data.copy(), reach_data=
            reach_data.copy())
            # add pods from Val (state board)
            reach_data, segment_data = self.add_pods_from_state_board(segment_data=segment_data.copy(), reach_data=
            reach_data.copy())

            n_segments = len(segment_data['nseg'].unique())
            n_reaches = len(reach_data)

        # The Segments information can be changed with time
        dataset_5 = {}
        nper = self.mf.dis.nper
        for i in np.arange(nper):  # we have only two stress period
            if i == 0:
                tss_par = n_segments
            else:
                tss_par = -1  # the negative sign indicates that segment data from previous time step will be used
            dataset_5[i] = [tss_par, 0, 0]

        # channel flow data
        channel_flow_data = {}  # for 6e - flow table [flow1 flow2; depth1, depth2, width1, width2]

        channel_geometry_data = {}  # 6d - complex channel cross-section
        # The flopy needs reach data and segment data as numpy recarray data structure
        ### There is a bug in flopy here.... to avoid the error sort data
        reach_data = reach_data.sort_values(by=['iseg', 'ireach'])
        segment_data = segment_data.sort_values(by=['nseg'])

        reach_data, segment_data, channel_flow_data = self.sfr_cross_sections(reach_data, segment_data)
        ## nstrpts = 0  greater thatn 0 is used when icalc=4 to determine the size of
        for iseg in channel_flow_data[0].keys():
            vall = len(channel_flow_data[0][iseg][0])
            segment_data.loc[segment_data['nseg'] == iseg, 'nstrpts'] = vall

        segment_data, reach_data, channel_flow_data = self.gates_calc(segment_data,
                                                                      reach_data, channel_flow_data)

        segment_data, reach_data = self.spillway_calc(segment_data, reach_data)

        # Tabfiles
        tabfiles = True
        tabfiles_dict = {}
        tabfiles_dict, average_inflows = self.compute_sfr_inflow()

        reach_data.slope[reach_data.slope <= 0] = 0.02
        segment_data_ss, reach_data_ss = self.Steady_state_SFR_changes(segment_data.copy(), reach_data.copy(),
                                                                       average_inflows)

        reach_data = reach_data.to_records(index=False)
        segment_data = segment_data.to_records(index=False)
        segment_data = {0: segment_data}
        # you can change segments data for each stress period? segment_data = {0: segment_data0, 1: segment_data1 }

        sfr = flopy.modflow.ModflowSfr2(self.mf, nstrm=n_reaches, nss=n_segments, const=const, nsfrpar=nsfrpar,
                                        nparseg=nparseg,
                                        dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
                                        istcb2=istcb2, reachinput=True, isfropt=isfropt, irtflg=irtflg,
                                        reach_data=reach_data, numtim=numtim, weight=weight,
                                        segment_data=segment_data, tabfiles=tabfiles, tabfiles_dict=tabfiles_dict,
                                        channel_geometry_data=channel_geometry_data,
                                        channel_flow_data=channel_flow_data,
                                        dataset_5=dataset_5, options=options)
        # self.mf.write_input()

        if True:
            segment_data_ss = self.compute_ag_diversions2(segment_data_ss)

        reach_data_ss = reach_data_ss.to_records(index=False)
        segment_data_ss = segment_data_ss.to_records(index=False)
        segment_data_ss = {0: segment_data_ss}
        options.tabfiles = False

        sfrs = flopy.modflow.ModflowSfr2(self.mfs, nstrm=n_reaches, nss=n_segments, const=const, nsfrpar=nsfrpar,
                                         nparseg=nparseg,
                                         dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
                                         istcb2=istcb2, reachinput=True, isfropt=isfropt, irtflg=irtflg,
                                         reach_data=reach_data_ss, numtim=numtim, weight=weight,
                                         segment_data=segment_data_ss,
                                         channel_geometry_data=channel_geometry_data,
                                         channel_flow_data=channel_flow_data,
                                         dataset_5=dataset_5, options=options)

    def strtop_correction(self, segment_data, reach_data):

        # read in table of lidar and dem_adj comparisons
        sfr_lidar = self.config.get('SFR', 'sfr_lidar')
        sfr_lidar = pd.read_csv(sfr_lidar)

        # read in dis elevations
        # TODO: check whether this should be self.mf.dis.top and all the other layers in the same fashion - ask Ayman
        grid = self.grid_3d

        # identify segments and reaches that need to be changed
        # note: don't raise the elevation of any segments
        mask = (sfr_lidar['Stage_Elev'] < sfr_lidar['Mean_DEM_ADJ'])
        sfr_lidar = sfr_lidar[mask]
        k_i_j = reach_data[['k', 'i', 'j']]
        k_i_j = k_i_j.astype(int)
        k_i_j = k_i_j.values

        # extract elevations of reaches that need to be changed and add to reach_data data frame
        for lay in range(grid.shape[0]):
            cell_sfr_botm = grid[lay, k_i_j[:, 1], k_i_j[:, 2]]
            reach_data['elev_{}'.format(lay)] = cell_sfr_botm

        # make changes to strtop
        for irec, rec in sfr_lidar.iterrows():

            # identify reaches to be changed
            iseg_mask = reach_data['iseg'] == rec['ISEG']

            # for each reach in which lidar < mean_dem_adj, set strtop = strtop - abs(lidar - mean_dem_adj) - 1
            # note: subtracting 1 m to account for water depth
            reach_data.loc[iseg_mask, 'strtop'] = reach_data.loc[iseg_mask, 'strtop'] - abs(rec['diff']) - 1.0

        # compare strtop to dis elevation and change layer if necessary
        for lay in range(self.mf.nlay):
            top = 'elev_{}'.format(lay)
            bot = 'elev_{}'.format(lay + 1)
            mask_elev = (reach_data['strtop'] <= reach_data[top]) & (reach_data['strtop'] > reach_data[bot])
            reach_data.loc[mask_elev, 'k'] = lay

        # delete added columns
        for lay in range(grid.shape[0]):
            del(reach_data['elev_{}'.format(lay)])

        # check to make sure that we still have continuously decreasing strtop values as we
        # move downstream after these changes
        # problem_reaches = pd.DataFrame(
        #     columns=['iseg', 'ireach', 'outseg', 'strtop_iseg', 'strtop_outseg', 'strtop_diff', 'iseg_strtop_lowered'])
        # problem_reaches_idx = 0
        # for i in range(len(segment_data)):
        #
        #     # for each iseg, store iupseg and outseg
        #     this_iseg = segment_data.loc[i, 'nseg']
        #     this_outseg = segment_data.loc[i, 'outseg']
        #
        #     # for each iseg, grab the reach data for the iseg
        #     df_iseg = reach_data.loc[reach_data['iseg'] == this_iseg].reset_index(drop=True)
        #
        #     # for each iseg, grab the reach data for its outseg and store the strtop of the most upstream reach
        #     if this_outseg > 0:
        #         df_outseg = reach_data.loc[reach_data['iseg'] == this_outseg].reset_index(drop=True)
        #         outseg_upstream_reach = df_outseg[df_outseg['ireach'] == min(df_outseg['ireach'])].reset_index(
        #             drop=True)
        #         outseg_upstream_reach = outseg_upstream_reach['strtop'][0]
        #     elif this_outseg < 0:
        #         outseg_upstream_reach = -9999
        #
        #     # check whether this is a segment we've altered
        #     if this_iseg in sfr_lidar['ISEG']:
        #         iseg_strtop_lowered_val = True
        #     else:
        #         iseg_strtop_lowered_val = False
        #
        #     # compare reach strtop values and store the iseg and ireach for any reaches that don't meet the criteria
        #     for j in range(len(df_iseg)):
        #
        #         # compare with downstream reach
        #         # TODO: max won't work when a segment only has one value in it, so need to come up with a different condition?
        #         if len(df_iseg) == 1 & int(this_outseg) > 0:
        #             if df_iseg.loc[j, 'strtop'] < outseg_upstream_reach:
        #                 strtop_iseg = df_iseg.loc[j, 'strtop']
        #                 strtop_outseg = outseg_upstream_reach
        #                 strtop_diff = strtop_iseg - strtop_outseg
        #                 problem_reaches.loc[problem_reaches_idx] = [this_iseg, df_iseg.loc[j, 'ireach'], this_outseg,
        #                                                             strtop_iseg, strtop_outseg, strtop_diff,
        #                                                             iseg_strtop_lowered_val]
        #                 problem_reaches_idx = problem_reaches_idx + 1
        #         elif j == int(max(df_iseg['ireach']) - 1) & int(this_outseg) > 0:
        #             if df_iseg.loc[j, 'strtop'] < outseg_upstream_reach:
        #                 strtop_iseg = df_iseg.loc[j, 'strtop']
        #                 strtop_outseg = outseg_upstream_reach
        #                 strtop_diff = strtop_iseg - strtop_outseg
        #                 problem_reaches.loc[problem_reaches_idx] = [this_iseg, df_iseg.loc[j, 'ireach'], this_outseg,
        #                                                             strtop_iseg, strtop_outseg, strtop_diff,
        #                                                             iseg_strtop_lowered_val]
        #                 problem_reaches_idx = problem_reaches_idx + 1
        #         elif j < int(max(df_iseg['ireach']) - 1):
        #             if df_iseg.loc[j, 'strtop'] < df_iseg.loc[j + 1, 'strtop']:
        #                 strtop_iseg = df_iseg.loc[j, 'strtop']
        #                 strtop_outseg = df_iseg.loc[j + 1, 'strtop']
        #                 strtop_diff = strtop_iseg - strtop_outseg
        #                 problem_reaches.loc[problem_reaches_idx] = [this_iseg, df_iseg.loc[i, 'ireach'], this_outseg,
        #                                                             strtop_iseg, strtop_outseg, strtop_diff,
        #                                                             iseg_strtop_lowered_val]
        #                 problem_reaches_idx = problem_reaches_idx + 1
        #
        # # export csv of problem_reaches
        # model_ws_tr = self.config.get('General_info', 'work_space')
        # file_name = os.path.join(model_ws_tr, 'other_files', 'test', 'problem_reaches.csv')
        # problem_reaches.to_csv(file_name)

        return (reach_data)

    def add_rubber_dam_sfr(self, segment_data, reach_data, tabfiles_dict, average_inflows):

        # ---- Grab variables from config file --------------------------------------------

        seg_id = self.config.get('RUBBER_DAM', 'seg_id_under_rubber_dam')
        seg_id = seg_id.split(',')
        seg_id = [int(ss) for ss in seg_id]

        new_outseg = self.config.get('RUBBER_DAM', 'new_outseg_under_rubber_dam')
        new_outseg = new_outseg.split(',')
        new_outseg = [int(ss) for ss in new_outseg]

        new_iupseg = self.config.get('RUBBER_DAM', 'new_iupseg_under_rubber_dam')
        new_iupseg = new_iupseg.split(',')
        new_iupseg = [int(ss) for ss in new_iupseg]

        rubber_dam_lake_id = self.config.get('RUBBER_DAM', 'rubber_dam_lake_id')
        rubber_dam_lake_id = int(rubber_dam_lake_id)

        rubber_dam_lake = self.config.get('RUBBER_DAM', 'rubber_dam_lake')
        rubber_dam_lake = geopandas.read_file(rubber_dam_lake)

        # ---- Set strtop equal to elevation of top of layer 1 in rubber dam lake grid cells --------------------------------------------

        # get top of layer 1 elevations
        grid = self.mf.dis.top

        # identify rubber dam lake reach row and col
        for irec, rec in rubber_dam_lake.iterrows():

            if rec['ISEG'] > 0:

                # identify rubber dam reach within reach_data
                reach_mask = (reach_data['iseg'] == rec['ISEG']) & (reach_data['ireach'] == rec['IREACH'])

                # get its top of layer 1 elevation
                hru_row = rec['HRU_ROW']
                hru_col = rec['HRU_COL']
                elev_top_lay1 = grid[hru_row - 1, hru_col - 1]

                # assign to strtop
                reach_data.loc[reach_mask, 'strtop'] = elev_top_lay1



        # ---- Function to change iupseg and outseg --------------------------------------------

        # Define function
        def change_iupseg_outseg(segment_data, seg_id, new_outseg, new_iupseg):

            # loop through segments and replace values
            for i in range(len(seg_id)):
                # identify index of segment to be changed
                seg_idx = segment_data[segment_data['nseg'] == seg_id[i]].index

                # change iupseg
                segment_data.loc[seg_idx, 'iupseg'] = new_iupseg[i]

                # change outseg
                segment_data.loc[seg_idx, 'outseg'] = new_outseg[i]

            return segment_data

        # Run function
        segment_data = change_iupseg_outseg(segment_data, seg_id, new_outseg, new_iupseg)

        # ---- Function to set streambed conductivities to 0 for all reaches affected by lake 12 -------------------

        # Define function
        def change_streambed_K(reach_data, rubber_dam_lake):

            # get segments and reaches to be changed
            seg_id = rubber_dam_lake["ISEG"]
            reach_id = rubber_dam_lake["IREACH"]

            # loop through segments and replace all values in their reaches
            for i in range(len(seg_id)):

                # if it's a stream segment
                if seg_id[i] > 0:
                    # identify index of reach to be changed
                    reach_idx = reach_data[
                        (reach_data['iseg'] == seg_id[i]) & (reach_data['ireach'] == reach_id[i])].index

                    # change streambed conductivity for this reach
                    reach_data.loc[reach_idx, 'strhc1'] = 0

            return reach_data

        # Run function
        reach_data = change_streambed_K(reach_data, rubber_dam_lake)

        # ---- Function to add two ouflow segments for the rubber dam --------------------------------------------

        # Define function
        def add_rubber_dam_gate_spillway(segment_data, reach_data, rubber_dam_lake_id):

            # set gate_iseg and spill_iseg
            n_seg = len(segment_data)
            gate_iseg = n_seg + 1
            spill_iseg = gate_iseg + 1

            # get segment and reach data for rubber dam gate and spillway segment outseg segment
            gate_outseg = self.config.get('RUBBER_DAM', 'rubber_dam_outseg_gate_spill')
            gate_outseg_segdata = segment_data[segment_data['nseg'] == float(gate_outseg)]
            gate_outseg_reachdata = reach_data[(reach_data['iseg'] == float(gate_outseg)) & (reach_data['ireach'] == 1)]

            # set dam inflated and deflated elevations in meters
            dam_inflated = float(self.config.get('RUBBER_DAM', 'rubber_dam_max_lake_stage'))
            dam_deflated = float(self.config.get('RUBBER_DAM', 'rubber_dam_min_lake_stage'))

            # calculate gate strtop and make sure it is higher than first reach of downstream segment
            gate_slope = gate_outseg_reachdata['slope'].values[0]
            #gate_rchlen = gate_outseg_reachdata['rchlen'].values[0]
            gate_rchlen = 400
            lake_bottom_buffer = 2
            gate_strtop = (dam_deflated + lake_bottom_buffer) - gate_slope * (0.5 * gate_rchlen)
            if gate_strtop < gate_outseg_reachdata['strtop'].values[0]:
                gate_strtop = gate_outseg_reachdata['strtop'].values[0] + 0.1

            # calculate spillway strtop and make sure it is higher than first reach of downstream segment
            #spillway_slope = 0.1
            spillway_slope = gate_outseg_reachdata['slope'].values[0]
            spillway_rchlen = 400
            spillway_strtop = dam_inflated - (spillway_slope * (0.5 * spillway_rchlen))
            if spillway_strtop < gate_outseg_reachdata['strtop'].values[0]:
                spillway_strtop = gate_outseg_reachdata['strtop'].values[0] + 0.1

            # fill in segment data for rubber dam gate and spillway
            gate_seg = {
                'nseg': gate_iseg,
                'icalc': 1,
                'outseg': gate_outseg,
                'iupseg': -1 * rubber_dam_lake_id,
                'iprior': 0,
                'nstrpts': 0,
                'flow': 0,
                'runoff': 0,
                'etsw': 0,
                'pptsw': 0,
                'roughch': 0.035,
                'roughbk': 0,
                'cdpth': 0,
                'fdpth': 0,
                'awdth': 0,
                'bwdth': 0,
                'hcond1': 0,
                'thickm1': 0,
                'elevup': 0,
                'width1': gate_outseg_segdata['width1'].values[0],
                'depth1': 0,
                'hcond2': 0,
                'thickm2': 0,
                'elevdn': 0,
                'width2': gate_outseg_segdata['width2'].values[0],
                'depth2': 0
            }

            spill_seg = {
                'nseg': spill_iseg,
                'icalc': 1,
                'outseg': self.config.get('RUBBER_DAM', 'rubber_dam_outseg_gate_spill'),
                'iupseg': -1 * rubber_dam_lake_id,
                'iprior': 0,
                'nstrpts': 0,
                'flow': 0,
                'runoff': 0,
                'etsw': 0,
                'pptsw': 0,
                'roughch': 0.035,
                'roughbk': 0,
                'cdpth': 0,
                'fdpth': 0,
                'awdth': 0,
                'bwdth': 0,
                'hcond1': 0,
                'thickm1': 0,
                'elevup': 0,
                'width1': 50,
                'depth1': 0,
                'hcond2': 0,
                'thickm2': 0,
                'elevdn': 0,
                'width2': 50,
                'depth2': 0
            }
            segment_data = segment_data.append(gate_seg, ignore_index=True)
            segment_data = segment_data.append(spill_seg, ignore_index=True)

            # fill in reach data for rubber dam gate and spillway
            gate_reach = {'node': np.nan,
                          'k': 1,  # assigned by comparing strtop to elevations of each layer from dis file
                          'i': int(self.config.get('RUBBER_DAM', 'rubber_dam_hru_row_gate')) - 1,
                          # subtracted 1 to be zero-based
                          'j': int(self.config.get('RUBBER_DAM', 'rubber_dam_hru_col_gate')) - 1,
                          # subtracted 1 to be zero-based
                          'iseg': gate_iseg,
                          'ireach': 1,
                          'rchlen': gate_rchlen,
                          'strtop': gate_strtop,
                          'slope': gate_slope,
                          'strthick': 0.5,
                          'strhc1': 0,
                          'thts': 0.310,
                          'thti': 0.131,
                          'eps': 3.5,
                          'uhc': 0.1,
                          'reachID': np.nan,
                          'outreach': np.nan}
            spill_reach = {'node': np.nan,
                           'k': 1,
                           'i': int(self.config.get('RUBBER_DAM', 'rubber_dam_hru_row_spill')) - 1,
                           # subtracted 1 to be zero-based,
                           'j': int(self.config.get('RUBBER_DAM', 'rubber_dam_hru_col_spill')) - 1,
                           # subtracted 1 to be zero-based,
                           'iseg': spill_iseg,
                           'ireach': 1,
                           'rchlen': spillway_rchlen,
                           'strtop': spillway_strtop,
                           'slope': spillway_slope,
                           'strthick': 0.5,
                           'strhc1': 0,
                           'thts': 0.310,
                           'thti': 0.131,
                           'eps': 3.5,
                           'uhc': 0.1,
                           'reachID': np.nan,
                           'outreach': np.nan}
            reach_data = reach_data.append(gate_reach, ignore_index=True)
            reach_data = reach_data.append(spill_reach, ignore_index=True)

            # return
            return segment_data, reach_data, gate_iseg, spill_iseg

        # Run function
        segment_data, reach_data, gate_iseg, spill_iseg = add_rubber_dam_gate_spillway(segment_data, reach_data,
                                                                                       rubber_dam_lake_id)

        # ---- Function to create gate and spillway tabfiles --------------------------------------------

        def create_gate_spillway_tabfiles(spill_iseg, gate_iseg, tabfiles_dict, average_inflows):

            # TODO: make this function cleaner by looping through separate spillway and gate data frames
            #  to export tabfiles and average inflows

            # TODO: export a plot of the rubber dam inflation/deflation dates superimposed
            #  on top of the full water surface elevation dataset

            # # read in dam water surface elevation data
            # file_name = self.config.get('RUBBER_DAM', 'rubber_dam_water_surface_elevation_file')
            # df = pd.read_excel(file_name, sheet_name='Data')
            # df.plot(x="date", y="wse_ft")

            # # set water surface elevations in winter months to 27 ft
            # df['month'] = df['date'].dt.month
            # month_idx = df[ (df['month'] == 1) | (df['month'] == 2) | (df['month'] == 3) |
            #     (df['month'] == 4) ].index
            # df.loc[month_idx, 'wse_ft'] = 27
            # df.plot(x="date", y="wse_ft")

            # # set water surface elevations over 40 ft to 27 ft
            # idx = df[ df['wse_ft'] > 40 ].index
            # df.loc[idx, 'wse_ft'] = 27
            # df.plot(x="date", y="wse_ft")

            # determine dates of dam inflation/deflation programmatically from data
            # Method 1: identify first and last 38 ft water level for each year or water year - but this will
            # catch the times when the dam is down too
            # Method 2: smooth the time series and then take the derivative - but this will not be precise
            # NOTE: not sure of the best way to do this to programmatically get precise dates of dam inflation/deflation
            # so just extracted them manually for now since it's quick and this dataset is unlikely to change for now -
            # could do it programmatically in the future if it turns out that precision doesn't matter that much

            # read in dates of dam inflation/deflation
            # NOTE: determined dates of dam inflation/deflation manually from data
            # NOTE: dam is probably inflated beyond 12/31/2020, but that is the end of the currently available data
            # (and possibly the end of the model calibration period?)
            inflated_dates_readin = self.config.get('RUBBER_DAM', 'inflated_dates')
            inflated_dates_readin = inflated_dates_readin.split(',')
            inflated_dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in inflated_dates_readin]
            deflated_dates_readin = self.config.get('RUBBER_DAM', 'deflated_dates')
            deflated_dates_readin = deflated_dates_readin.split(',')
            deflated_dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in deflated_dates_readin]

            # use pattern from data to extrapolate dam inflation/deflation dates to rest of model calibration period
            # NOTE: inflation date varies from March-July and deflation date varies from December-February, for
            # now just assuming that average inflation date is in mid-June and average deflation date is in mid-December
            # in order to extrapolate to years with no data
            average_inflated_date = self.config.get('RUBBER_DAM', 'average_inflated_date')
            average_deflated_date = self.config.get('RUBBER_DAM', 'average_deflated_date')
            min_extrapolated_year = 1990
            max_extrapolated_year = 2007
            years_extrapolated = list(map(str, range(min_extrapolated_year, max_extrapolated_year + 1)))
            inflated_dates_extrapolated = [year + average_inflated_date for year in years_extrapolated]
            deflated_dates_extrapolated = [year + average_deflated_date for year in years_extrapolated]
            inflated_dates_extrapolated = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in
                                           inflated_dates_extrapolated]
            deflated_dates_extrapolated = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in
                                           deflated_dates_extrapolated]

            # combine observed and extrapolated dates
            inflated_dates = pd.to_datetime(inflated_dates_extrapolated + inflated_dates)
            deflated_dates = pd.to_datetime(deflated_dates_extrapolated + deflated_dates)

            # set values of gate and spillway tabfiles based on whether dam is inflated or deflated
            # dam inflated --> spillway is 0 and gate is 1e-5
            # dam deflated --> spillway is 1e-5 and gate is 0
            # create time series from 1990-01-01 to 2020-12-31
            start_date = datetime.datetime.strptime("1990-01-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime("2020-12-31", "%Y-%m-%d")
            calib_dates = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
            df = {'date': pd.to_datetime(calib_dates),
                  'sim_time': [x + 1 for x in list(range(len(calib_dates)))],
                  'dam_elev': 27,  # set to the value it should have if dam is deflated
                  'spillway_flow': 1e-5,  # set to the value it should have if dam is deflated
                  'gate_flow': 0}  # set to the value it should have if dam is deflated
            df = pd.DataFrame(df, columns=['date', 'sim_time', 'dam_elev', 'spillway_flow', 'gate_flow'])

            # loop through each value of inflated_dates and deflated_dates
            for i in range(len(inflated_dates)):
                # identify indices of rows with inflated dam
                inflated_idx = df[(df['date'] >= inflated_dates[i]) & (df['date'] <= deflated_dates[i])].index

                # replace values for spillway and gate tabfiles along with dam elevation
                df.loc[inflated_idx, 'dam_elev'] = 38
                df.loc[inflated_idx, 'spillway_flow'] = 0
                df.loc[inflated_idx, 'gate_flow'] = 1e-5

            # prepare to export tabfiles
            # tabfiles_dict = {}
            # average_inflows = {}
            model_ws_tr = self.config.get('General_info', 'work_space')
            model_ws_tr = os.path.join(model_ws_tr, 'tr')
            model_ws_ss = self.config.get('General_info', 'work_space')
            model_ws_ss = os.path.join(model_ws_ss, 'ss')

            # export spillway tabfile
            rubber_dam_spillway_tabfile = self.config.get('RUBBER_DAM', 'rubber_dam_spillway_tabfile')
            fn = os.path.join(model_ws_tr, rubber_dam_spillway_tabfile)
            fid = open(fn, 'w')
            for i in range(len(df)):
                fid.write(str(df.loc[i, 'sim_time']))
                fid.write(" ")
                fid.write(str(df.loc[i, 'spillway_flow']))
                fid.write(" #")
                fid.write(str(df.loc[i, 'date']))
                fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for spillway
            numval = len(df)
            iunit = self.mf.next_ext_unit()
            self.mf.external_units.append(iunit)
            self.mf.external_fnames.append(os.path.basename(fn))
            self.mf.external_binflag.append(False)
            tabfiles_dict[spill_iseg] = {'numval': numval, 'inuit': iunit}

            # export gate tabfile
            rubber_dam_gate_tabfile = self.config.get('RUBBER_DAM', 'rubber_dam_gate_tabfile')
            fn = os.path.join(model_ws_tr, rubber_dam_gate_tabfile)
            fid = open(fn, 'w')
            for i in range(len(df)):
                fid.write(str(df.loc[i, 'sim_time']))
                fid.write(" ")
                fid.write(str(df.loc[i, 'gate_flow']))
                fid.write(" #")
                fid.write(str(df.loc[i, 'date']))
                fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for gate
            numval = len(df)
            iunit = self.mf.next_ext_unit()
            self.mf.external_units.append(iunit)
            self.mf.external_fnames.append(os.path.basename(fn))
            self.mf.external_binflag.append(False)
            tabfiles_dict[gate_iseg] = {'numval': numval, 'inuit': iunit}

            # create dictionary for steady state tabfiles
            tabfiles_dict_ss = {}

            # export spillway tabfile - steady state
            rubber_dam_spillway_tabfile_ss = self.config.get('RUBBER_DAM', 'rubber_dam_spillway_tabfile_ss')
            rubber_dam_spillway_tabfile_ss_flow = self.config.get('RUBBER_DAM', 'rubber_dam_spillway_tabfile_ss_flow')
            fn = os.path.join(model_ws_ss, rubber_dam_spillway_tabfile_ss)
            fid = open(fn, 'w')
            fid.write(str(0))
            fid.write(" ")
            fid.write(rubber_dam_spillway_tabfile_ss_flow)
            fid.write("\n")
            fid.write(str(1))
            fid.write(" ")
            fid.write(rubber_dam_spillway_tabfile_ss_flow)
            fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for spillway - steady state
            numval = 2
            iunit = self.mfs.next_ext_unit()
            #iunit = 2001
            self.mfs.external_units.append(iunit)
            self.mfs.external_fnames.append(os.path.basename(fn))
            self.mfs.external_binflag.append(False)
            tabfiles_dict_ss[spill_iseg] = {'numval': numval, 'inuit': iunit}

            # export gate tabfile - steady state
            rubber_dam_gate_tabfile_ss = self.config.get('RUBBER_DAM', 'rubber_dam_gate_tabfile_ss')
            rubber_dam_gate_tabfile_ss_flow = self.config.get('RUBBER_DAM', 'rubber_dam_gate_tabfile_ss_flow')
            fn = os.path.join(model_ws_ss, rubber_dam_gate_tabfile_ss)
            fid = open(fn, 'w')
            fid.write(str(0))
            fid.write(" ")
            fid.write(rubber_dam_gate_tabfile_ss_flow)
            fid.write("\n")
            fid.write(str(1))
            fid.write(" ")
            fid.write(rubber_dam_gate_tabfile_ss_flow)
            fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for gate - steady state
            numval = 2
            iunit = self.mfs.next_ext_unit()
            #iunit = 2002
            self.mfs.external_units.append(iunit)
            self.mfs.external_fnames.append(os.path.basename(fn))
            self.mfs.external_binflag.append(False)
            tabfiles_dict_ss[gate_iseg] = {'numval': numval, 'inuit': iunit}

            # set outflows for steady state model
            average_inflows[spill_iseg] = 1e-5
            average_inflows[gate_iseg] = 0

            return tabfiles_dict, tabfiles_dict_ss, average_inflows

        # Run function
        tabfiles_dict, tabfiles_dict_ss, average_inflows = create_gate_spillway_tabfiles(spill_iseg, gate_iseg, tabfiles_dict,
                                                                       average_inflows)

        # ---- Function to add an outflow segment to the nearby ponds from the rubber dam ------------------------------

        def add_rubber_dam_outflow_to_ponds(segment_data, reach_data, rubber_dam_lake_id, tabfiles_dict_ss):

            # TODO: check whether the rubber dam pond outflow segment should be made similar to the gate or
            #  spillway segments, for now making it different since it has no outseg from which to grab data

            # set pond outflow iseg
            n_seg = len(segment_data)
            pond_outflow_iseg = n_seg + 1

            # read in
            # pond_outflow_iseg = int(self.config.get('RUBBER_DAM', 'pond_outflow_iseg'))
            pond_outflow_width = float(self.config.get('RUBBER_DAM', 'pond_outflow_width'))

            # calculate pond outflow strtop and slope
            dam_deflated = float(self.config.get('RUBBER_DAM', 'rubber_dam_min_lake_stage'))
            lake_bottom_buffer = 2
            cell_size = 300
            pond_outflow_strtop = (dam_deflated + lake_bottom_buffer) - 1
            pond_outflow_slope = ((dam_deflated + lake_bottom_buffer) - (pond_outflow_strtop)) / (cell_size / 2)

            # fill in segment data for pond outflow
            pond_outflow_seg = {
                'nseg': pond_outflow_iseg,
                'icalc': 1,
                'outseg': 0,
                'iupseg': -1 * rubber_dam_lake_id,
                'iprior': 0,
                'nstrpts': 0,
                'flow': 0,
                'runoff': 0,
                'etsw': 0,
                'pptsw': 0,
                'roughch': 0.035,
                'roughbk': 0,
                'cdpth': 0,
                'fdpth': 0,
                'awdth': 0,
                'bwdth': 0,
                'hcond1': 0,
                'thickm1': 0,
                'elevup': 0,
                'width1': pond_outflow_width,
                'depth1': 0,
                'hcond2': 0,
                'thickm2': 0,
                'elevdn': 0,
                'width2': pond_outflow_width,
                'depth2': 0
            }
            segment_data = segment_data.append(pond_outflow_seg, ignore_index=True)

            # fill in reach data for pond outflow
            pond_outflow_reach = {'node': np.nan,
                                  'k': 1,  # assigned by comparing strtop to elevations of each layer from dis file
                                  'i': int(self.config.get('RUBBER_DAM', 'pond_outflow_hru_row')) - 1,
                                  # subtracted 1 to be zero-based
                                  'j': int(self.config.get('RUBBER_DAM', 'pond_outflow_hru_col')) - 1,
                                  # subtracted 1 to be zero-based
                                  'iseg': pond_outflow_iseg,
                                  'ireach': 1,
                                  'rchlen': cell_size,
                                  'strtop': pond_outflow_strtop,
                                  'slope': pond_outflow_slope,
                                  'strthick': 0.5,
                                  'strhc1': 0,
                                  'thts': 0.310,
                                  'thti': 0.131,
                                  'eps': 3.5,
                                  'uhc': 0.1,
                                  'reachID': np.nan,
                                  'outreach': np.nan}
            reach_data = reach_data.append(pond_outflow_reach, ignore_index=True)

            # prepare to export tabfiles
            model_ws_tr = self.config.get('General_info', 'work_space')
            model_ws_tr = os.path.join(model_ws_tr, 'tr')
            model_ws_ss = self.config.get('General_info', 'work_space')
            model_ws_ss = os.path.join(model_ws_ss, 'ss')

            # prepare data frame of transient pond outflow values
            start_date = datetime.datetime.strptime("1990-01-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime("2020-12-31", "%Y-%m-%d")
            calib_dates = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
            df = {'date': pd.to_datetime(calib_dates),
                  'sim_time': [x + 1 for x in list(range(len(calib_dates)))],
                  'pond_flow': float(self.config.get('RUBBER_DAM', 'rubber_dam_pond_tabfile_flow')) }
            df = pd.DataFrame(df, columns=['date', 'sim_time', 'pond_flow'])

            # make transient tabfile
            rubber_dam_pond_tabfile = self.config.get('RUBBER_DAM', 'rubber_dam_pond_tabfile')
            fn = os.path.join(model_ws_tr, rubber_dam_pond_tabfile)
            fid = open(fn, 'w')
            for i in range(len(df)):
                fid.write(str(df.loc[i, 'sim_time']))
                fid.write(" ")
                fid.write(str(df.loc[i, 'pond_flow']))
                fid.write(" #")
                fid.write(str(df.loc[i, 'date']))
                fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for pond outflow - transient
            numval = len(df)
            iunit = self.mf.next_ext_unit()
            self.mf.external_units.append(iunit)
            self.mf.external_fnames.append(os.path.basename(fn))
            self.mf.external_binflag.append(False)
            tabfiles_dict[spill_iseg] = {'numval': numval, 'inuit': iunit}

            # make steady state tabfile
            rubber_dam_pond_tabfile_ss = self.config.get('RUBBER_DAM', 'rubber_dam_pond_tabfile_ss')
            rubber_dam_pond_tabfile_ss_flow = self.config.get('RUBBER_DAM', 'rubber_dam_pond_tabfile_ss_flow')
            fn = os.path.join(model_ws_ss, rubber_dam_pond_tabfile_ss)
            fid = open(fn, 'w')
            fid.write(str(0))
            fid.write(" ")
            fid.write(rubber_dam_pond_tabfile_ss_flow)
            fid.write("\n")
            fid.write(str(1))
            fid.write(" ")
            fid.write(rubber_dam_pond_tabfile_ss_flow)
            fid.write("\n")
            fid.close()

            # create tabfiles dictionary entry for pond outflow - steady state
            numval = 2
            iunit = self.mfs.next_ext_unit()
            self.mfs.external_units.append(iunit)
            self.mfs.external_fnames.append(os.path.basename(fn))
            self.mfs.external_binflag.append(False)
            tabfiles_dict_ss[gate_iseg] = {'numval': numval, 'inuit': iunit}

            # return
            return segment_data, reach_data, tabfiles_dict_ss

        # Run function
        segment_data, reach_data, tabfiles_dict_ss = add_rubber_dam_outflow_to_ponds(segment_data, reach_data, rubber_dam_lake_id, tabfiles_dict_ss)

        return segment_data, reach_data, tabfiles_dict, tabfiles_dict_ss, average_inflows

    def sfr3_package(self):

        # Import
        from flopy.utils.optionblock import OptionBlock

        # Create options block
        options = OptionBlock('', flopy.modflow.ModflowSfr2, block=True)
        options.reachinput = True  # False
        options.tabfiles = True

        # Read flow accumulation file
        flo_acc = self.config.get('SFR', 'str_flow_acc')
        sfr_with_floacc = geopandas.read_file(flo_acc)  #
        sfr_with_floacc = sfr_with_floacc.sort_values(by='HRU_ID')

        # Extract streams data from hru shapefile and add flow accumulation data to it
        hru_shp = self.hru_param
        mask = hru_shp['ISEG'] > 0
        streams_data = hru_shp[mask]  # a compact form is streams_data = hru_shp[hru_shp['ISEG'] > 0]
        streams_data = streams_data.sort_values(by='HRU_ID')
        streams_data['flow_accum'] = sfr_with_floacc['grid_code'].values

        # ---- Reach data -------------------------------------------------------------------------

        # NOTE: The reach data will be saved in a Pandas dataframe, which will make it simpler to handle the tabular data.

        # Reach data table field names
        reach_data_labels = ['node', 'k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope',
                             'strthick', 'strhc1', 'thts', 'thti', 'eps', 'uhc', 'reachID', 'outreach']

        # Initialize an empty pandas dataframe
        reach_data = pd.DataFrame(columns=reach_data_labels, dtype='float')

        # Reach location
        reach_data['k'] = 0  # layer number-- Notice that layer numbers are zero-based
        reach_data['i'] = streams_data['HRU_ROW'].values - 1  # row number
        reach_data['j'] = streams_data['HRU_COL'].values - 1  # column number

        # Assign layers IDs after making sure stream cells are in active zone
        for index, rech in reach_data.iterrows():  # get layer
            thk = self.mf.dis.thickness.array[:, int(rech['i']), int(rech['j'])]
            ibsfr = self.mf.bas6.ibound.array[:, int(rech['i']), int(rech['j'])]
            if sum(thk) == 0:
                raise ValueError("Stream in inactive zone")
            for kk, val in enumerate(thk):
                if val > 0 and ibsfr[kk]>0:
                    # reach_data.set_value(index, 'k', kk)
                    reach_data.at[index, 'k'] = kk
                    break
            pass

        # Reach IDs
        reach_data['iseg'] = streams_data['ISEG'].values  # Segment ID number
        reach_data['ireach'] = streams_data['IREACH'].values  # Reach ID number
        # reach_data['ireach'][reach_data['ireach'] < 1] = 1
        reach_data.loc[reach_data['ireach'] < 1, 'ireach'] = 1  # the newly added segments (div and spillways) has
        # ireach =0

        # Stream topography
        reach_data['rchlen'] = streams_data['RCHLEN'].values  # reach length
        reach_data.loc[reach_data['rchlen'] == 0, 'rchlen'] = 300.0
        reach_data['strtop'] = streams_data[
                                   'DEM_ADJ'].values - 1.0  # Streambed elevation is assumed 1 meter below ground surface.
        reach_data['slope'] = streams_data['DEM_SLP_P'].values  # / 100.0  # Slope #todo: divid by 100 is not correct!!

        # Streambed information
        reach_data['strthick'] = 0.5  # streambed thickness - meter
        reach_data['strhc1'] = 0.1  # conductivity of the stream bed

        # Unsaturated Zone properties
        reach_data['thts'] = 0.31  # saturated porosity
        reach_data['thti'] = 0.131  # initial water content
        reach_data['eps'] = 3.5  # Brooks-Corey exponent
        reach_data['uhc'] = 0.1  # conductivity of the unsaturated zone
        n_reaches = len(reach_data)  # number of reaches

        # calculate stream slope
        reach_data = self.calculate_stream_slope(reach_data)

        # ---- Segment data -------------------------------------------------------------------------

        # Segment data table field names
        seg_data_labels = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior',
                           'nstrpts', 'flow', 'runoff', 'etsw', 'pptsw', 'roughch', 'roughbk',
                           'cdpth', 'fdpth', 'awdth', 'bwdth', 'hcond1', 'thickm1',
                           'elevup', 'width1', 'depth1', 'hcond2', 'thickm2', 'elevdn',
                           'width2', 'depth2']

        # Compute width based on flow accumulation
        streams_data = self.cal_stream_width(streams_data, flo_acc)

        # Use the segment data from the HRU shapefile
        unique_segments = streams_data.drop_duplicates(['ISEG'], keep='first')
        unique_segments = unique_segments.sort_values(by='ISEG')

        # Extract number of segments
        n_segments = len(unique_segments)

        # Initialize dataframe filled with zeros
        zero_data = np.zeros((n_segments, len(seg_data_labels)))
        segment_data = pd.DataFrame(zero_data, columns=seg_data_labels, dtype='float')

        # Fill segments data frame
        segment_data['nseg'] = unique_segments['ISEG'].values  # Segment ID
        segment_data['icalc'] = 1  # Use Manning's Equation for a rectangular cross-section
        segment_data['outseg'] = unique_segments['OUTSEG'].values  # Downstream Segment
        segment_data['iupseg'] = unique_segments[
            'IUPSEG'].values  # segmet id for Upstream diversion or negative ID of the lake
        segment_data['width1'] = unique_segments['Width'].values  # Upstream width
        segment_data['width2'] = unique_segments['Width'].values  # Downstream width
        segment_data['roughch'] = float(self.config.get('SFR', 'mannings_roughness'))

        # ---- Assign options in the first line of SFR package ------------------------------------------------------

        nsfrpar = 0  # number of parameters
        nparseg = 0
        isfropt = 3  # uzf is simulated, k is read from uzf
        const = 86400  # constant for manning's equation, units of ??
        dleak = 0.0001  # closure tolerance for stream stage computation
        ipakcb = 55  # flag for writing SFR output to cell-by-cell budget (on unit 55)
        istcb2 = 81  # flag for writing SFR output to text file
        nstrail = 15  # used when USZ is simulated, number of trailing wave increments
        isuzn = 1  # used when USZ is simulated, number of vertical cells in unz, for icalc=1, isuzn = 1
        nsfrsets = 50  # used when USZ is simulated, number of sets of trailing wave
        irtflg = 0  # an integer value that flags whether transient streamflow routing is active
        numtim = 2  # used when irtflg > 0, number of sub time steps to route streamflow
        weight = 0.75  # used when irtflg > 0,A real number equal to the time weighting factor used to calculate the change in channel storage.

        # ---- Add ag diversions ---------------------------------------------------------------------

        if True:
            # todo: from now on we must slice hru_df and assign to reach_data
            reach_data = reach_data.reset_index()
            del (reach_data['index'])
            reach_data, segment_data = self.add_ag_full_diversions_segs(segment_data=segment_data.copy(), reach_data=
            reach_data.copy())
            # add pods from Val (state board)
            reach_data, segment_data = self.add_pods_from_state_board(segment_data=segment_data.copy(), reach_data=
            reach_data.copy())

            n_segments = len(segment_data['nseg'].unique())
            n_reaches = len(reach_data)

        # ---- Create sfr dataset 5 ------------------------------------------------------------------

        # NOTE: the Segments information can be changed with time (i.e. by stress period)

        dataset_5 = {}
        nper = self.mf.dis.nper
        for i in np.arange(nper):  # we have only two stress period
            if i == 0:
                tss_par = n_segments
            else:
                tss_par = -1  # the negative sign indicates that segment data from previous time step will be used
            dataset_5[i] = [tss_par, 0, 0]

        # ---- Create sfr datasets 6e and 6d ------------------------------------------------------------------

        # channel flow data
        channel_flow_data = {}  # for 6e - flow table [flow1 flow2; depth1, depth2, width1, width2]

        channel_geometry_data = {}  # 6d - complex channel cross-section
        # The flopy needs reach data and segment data as numpy recarray data structure
        ### There is a bug in flopy here.... to avoid the error sort data
        reach_data = reach_data.sort_values(by=['iseg', 'ireach'])
        segment_data = segment_data.sort_values(by=['nseg'])

        reach_data, segment_data, channel_flow_data = self.sfr_cross_sections(reach_data, segment_data)
        ## nstrpts = 0  greater thatn 0 is used when icalc=4 to determine the size of
        for iseg in channel_flow_data[0].keys():
            vall = len(channel_flow_data[0][iseg][0])
            segment_data.loc[segment_data['nseg'] == iseg, 'nstrpts'] = vall

        # ---- Assign lake gates and spillways ------------------------------------------------------------------

        segment_data, reach_data, channel_flow_data = self.gates_calc(segment_data,
                                                                      reach_data, channel_flow_data)

        segment_data, reach_data = self.spillway_calc(segment_data, reach_data)

        # ---- Tabfiles ------------------------------------------------------------------

        tabfiles = True
        tabfiles_dict = {}
        tabfiles_dict, average_inflows = self.compute_sfr_inflow()

        # ---- Streambed elevation (strtop) correction ------------------------------------------------------------------
        reach_data = self.strtop_correction(segment_data, reach_data)

        # ---- Incorporate rubber dam ------------------------------------------------------------------

        # run functions to incorporate rubber dam
        segment_data, reach_data, tabfiles_dict, tabfiles_dict_ss, average_inflows = self.add_rubber_dam_sfr(segment_data, reach_data,
                                                                                           tabfiles_dict, average_inflows)

        # update sfr dataset 5
        n_segments = len(segment_data['nseg'].unique())
        n_reaches = len(reach_data)
        dataset_5 = {}
        nper = self.mf.dis.nper
        for i in np.arange(nper):  # we have only two stress period
            if i == 0:
                tss_par = n_segments
            else:
                tss_par = -1  # the negative sign indicates that segment data from previous time step will be used
            dataset_5[i] = [tss_par, 0, 0]

        # ---- Slope correction ------------------------------------------------------------------

        # TODO: ask Ayman - do we want this slope correction to use min_slope to match up with the slope correction
        #  in the calculate_stream_slope() function? --> I'm assuming yes and changing it for now
        min_slope = float(self.config.get('SFR', 'min_slope'))
        # reach_data.slope[reach_data.slope <= 0] = 0.02
        reach_data.slope[reach_data.slope <= 0] = min_slope

        # ---- Make changes for steady state model ------------------------------------------------------------------

        segment_data_ss, reach_data_ss = self.Steady_state_SFR_changes(segment_data.copy(), reach_data.copy(),
                                                                       average_inflows)

        # ---- Write transient and steady state sfr packages ------------------------------------------------------------------

        # Prepare to write transient sfr package
        reach_data = reach_data.to_records(index=False)
        segment_data = segment_data.to_records(index=False)
        segment_data = {0: segment_data}
        # you can change segments data for each stress period? segment_data = {0: segment_data0, 1: segment_data1 }

        # Write transient SFR package
        sfr = flopy.modflow.ModflowSfr2(self.mf, nstrm=n_reaches, nss=n_segments, const=const, nsfrpar=nsfrpar,
                                        nparseg=nparseg,
                                        dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
                                        istcb2=istcb2, reachinput=True, isfropt=isfropt, irtflg=irtflg,
                                        reach_data=reach_data, numtim=numtim, weight=weight,
                                        segment_data=segment_data, tabfiles=tabfiles, tabfiles_dict=tabfiles_dict,
                                        channel_geometry_data=channel_geometry_data,
                                        channel_flow_data=channel_flow_data,
                                        dataset_5=dataset_5, options=options)
        # self.mf.write_input()

        # Compute ag diversions for steady state sfr package
        if True:
            segment_data_ss = self.compute_ag_diversions2(segment_data_ss)

        # Prepare to write steady state sfr package
        reach_data_ss = reach_data_ss.to_records(index=False)
        segment_data_ss = segment_data_ss.to_records(index=False)
        segment_data_ss = {0: segment_data_ss}
        #options.tabfiles = False

        # # Write steady state sfr package
        # sfrs = flopy.modflow.ModflowSfr2(self.mfs, nstrm=n_reaches, nss=n_segments, const=const, nsfrpar=nsfrpar,
        #                                  nparseg=nparseg,
        #                                  dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
        #                                  istcb2=istcb2, reachinput=True, isfropt=isfropt, irtflg=irtflg,
        #                                  reach_data=reach_data_ss, numtim=numtim, weight=weight,
        #                                  segment_data=segment_data_ss,
        #                                  channel_geometry_data=channel_geometry_data,
        #                                  channel_flow_data=channel_flow_data,
        #                                  dataset_5=dataset_5, options=options)
        # Write steady state sfr package
        sfrs = flopy.modflow.ModflowSfr2(self.mfs, nstrm=n_reaches, nss=n_segments, const=const, nsfrpar=nsfrpar,
                                         nparseg=nparseg,
                                         dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
                                         istcb2=istcb2, reachinput=True, isfropt=isfropt, irtflg=irtflg,
                                         reach_data=reach_data_ss, numtim=numtim, weight=weight,
                                         segment_data=segment_data_ss, tabfiles=tabfiles, tabfiles_dict=tabfiles_dict_ss,
                                         channel_geometry_data=channel_geometry_data,
                                         channel_flow_data=channel_flow_data,
                                         dataset_5=dataset_5, options=options)

    def add_pods_from_state_board(self, segment_data, reach_data):
        """
        This function adds the PODS that were sent to us from state board, so they have no diversions
        :param segment_data:
        :param reach_data:
        :return:
        """

        # 1) read state board (Val) pod shape file
        pod_file = self.config.get('SFR', 'stat_board_pods')
        max_seg_no = segment_data['nseg'].max()
        poddf = geopandas.read_file(pod_file)

        # find the closest stream to this pod
        uniq_seg = []
        for irec, rec in poddf.iterrows():
            pod_row = rec['HRU_ROW'] - 1
            pod_col = rec['HRU_COL'] - 1

            delrow = reach_data['i'].values - pod_row
            delcol = reach_data['j'].values - pod_col
            distt = np.power(delrow ** 2.0 + delcol ** 2.0, 0.5)
            locc = np.argmin(distt)
            close_seg = reach_data['iseg'].values[locc]
            uniq_seg.append(close_seg)

        curr_seg_no = max_seg_no
        for seg in uniq_seg:
            if np.any(segment_data['iupseg'].values == seg):
                # if there is a diversion seg that already exist, skip
                continue
            curr_seg_ifo = segment_data[segment_data['nseg'] == seg]
            if (curr_seg_ifo['outseg'].values[0] == 0) and (curr_seg_ifo['iupseg'].values[0] != 0):
                continue
            curr_seg_no = curr_seg_no + 1
            new_row_idex = curr_seg_no - 1
            segment_data.loc[new_row_idex] = segment_data.loc[0].values  # use default falues, and in next lines change
            segment_data.at[new_row_idex, 'nseg'] = curr_seg_no
            segment_data.at[new_row_idex, 'icalc'] = 1  # Use Manning's Equation for a rectangular cross-section
            segment_data.at[new_row_idex, 'outseg'] = 0
            segment_data.at[new_row_idex, 'iupseg'] = seg
            segment_data.at[new_row_idex, 'width1'] = 10.0  # Upstream width
            segment_data.at[new_row_idex, 'width2'] = 10.0  # Downstream width
            segment_data.at[new_row_idex, 'roughch'] = float(self.config.get('SFR', 'mannings_roughness'))

            # reach data
            mask_reach = reach_data['iseg'] == seg
            curr_rech_info = reach_data[mask_reach]
            dn_reach = np.max(curr_rech_info['ireach'].values)
            ii = curr_rech_info.loc[curr_rech_info['ireach'] == dn_reach, 'i'].values[0]
            jj = curr_rech_info.loc[curr_rech_info['ireach'] == dn_reach, 'j'].values[0]

            near_cells = [(ii - 1, jj),
                          (ii + 1, jj),
                          (ii, jj - 1),
                          (ii, jj + 1),
                          (ii - 1, jj + 1),
                          (ii - 1, jj - 1),
                          (ii + 1, jj + 1),
                          (ii + 1, jj - 1)]
            rr_cc = list(zip(reach_data['i'], reach_data['j']))
            for pp in near_cells:
                found = 0
                if not (pp in rr_cc):
                    found = 1
                    break
            if found == 0:
                raise ValueError("New stream is not found")

            irech = len(reach_data)
            reach_data.loc[irech] = reach_data.loc[0].values
            reach_data.at[irech, 'k'] = 0  # layer number-- Notice that layer numbers are zero-based
            reach_data.at[irech, 'i'] = pp[0]  # row number
            reach_data.at[irech, 'j'] = pp[1]  # column number
            try:
                thk = self.mf.dis.thickness.array[:, int(pp[0]), int(pp[1])]
            except:
                xxx = 1
            if sum(thk) == 0:
                raise ValueError("Stream in inactive zone")
            for kk, val in enumerate(thk):
                if val > 0:
                    # reach_data.set_value(index, 'k', kk)
                    reach_data.at[irech, 'k'] = kk
                    break
            pass
            # IDs
            reach_data.at[irech, 'iseg'] = curr_seg_no  # Segment ID number
            reach_data.at[irech, 'ireach'] = 1  # Reach ID number

            # Stream topography
            reach_data.at[irech, 'rchlen'] = 300.0  # reach length
            row_mask = self.hru_param['HRU_ROW'] == pp[0] + 1
            col_mask = self.hru_param['HRU_COL'] == pp[1] + 1
            cell_info = self.hru_param[(row_mask & col_mask)]
            reach_data.at[irech, 'strtop'] = cell_info['DEM_ADJ'].values[0] - 1.0  # Streambed elevation is assumed 1
            # meter
            # below ground surface.
            reach_data.at[irech, 'slope'] = cell_info['DEM_SLP_P'].values[0] / 100.0  # Slope

            # Streambed information
            reach_data.at[irech, 'strthick'] = 0.5  # streambed thickness - meter
            reach_data.at[irech, 'strhc1'] = 0.0  # conductivity of the stream bed

            # Unsaturated Zone properties
            reach_data.at[irech, 'thts'] = 0.31  # saturated porosity
            reach_data.at[irech, 'thti'] = 0.131  # initial water content
            reach_data.at[irech, 'eps'] = 3.5  # Brooks-Corey exponent
            reach_data.at[irech, 'uhc'] = 0.1  # conductivity of the unsaturated zone

        return reach_data, segment_data

    def add_ag_full_diversions_segs(self, segment_data, reach_data):
        """ Add new diversion segments for ag water diversion"""

        max_seg_no = segment_data['nseg'].max()

        # load diversion/field diversions
        pod_file = self.config.get('SFR', 'agg_pods_fields')
        poddf = pd.read_csv(pod_file)
        uniq_seg = poddf['ISEG'].unique()
        curr_seg_no = max_seg_no
        for seg in uniq_seg:
            if np.any(segment_data['iupseg'].values == seg):
                # if there is a diversion seg that already exist, skip
                continue
            curr_seg_ifo = segment_data[segment_data['nseg'] == seg]
            if (curr_seg_ifo['outseg'].values[0] == 0) and (curr_seg_ifo['iupseg'].values[0] != 0):
                continue

            curr_seg_no = curr_seg_no + 1
            new_row_idex = curr_seg_no - 1
            segment_data.loc[new_row_idex] = segment_data.loc[0].values  # use default falues, and in next lines change
            segment_data.at[new_row_idex, 'nseg'] = curr_seg_no
            segment_data.at[new_row_idex, 'icalc'] = 1  # Use Manning's Equation for a rectangular cross-section
            segment_data.at[new_row_idex, 'outseg'] = 0
            segment_data.at[new_row_idex, 'iupseg'] = seg
            segment_data.at[new_row_idex, 'width1'] = 10.0  # Upstream width
            segment_data.at[new_row_idex, 'width2'] = 10.0  # Downstream width
            segment_data.at[new_row_idex, 'roughch'] = float(self.config.get('SFR', 'mannings_roughness'))

            # reach data
            mask_reach = reach_data['iseg'] == seg
            curr_rech_info = reach_data[mask_reach]
            dn_reach = np.max(curr_rech_info['ireach'].values)
            ii = curr_rech_info.loc[curr_rech_info['ireach'] == dn_reach, 'i'].values[0]
            jj = curr_rech_info.loc[curr_rech_info['ireach'] == dn_reach, 'j'].values[0]

            near_cells = [(ii - 1, jj),
                          (ii + 1, jj),
                          (ii, jj - 1),
                          (ii, jj + 1),
                          (ii - 1, jj + 1),
                          (ii - 1, jj - 1),
                          (ii + 1, jj + 1),
                          (ii + 1, jj - 1)]
            rr_cc = list(zip(reach_data['i'], reach_data['j']))
            for pp in near_cells:
                found = 0
                if not (pp in rr_cc):
                    found = 1
                    break
            if found == 0:
                raise ValueError("New stream is not found")

            irech = len(reach_data)
            reach_data.loc[irech] = reach_data.loc[0].values
            reach_data.at[irech, 'k'] = 0  # layer number-- Notice that layer numbers are zero-based
            reach_data.at[irech, 'i'] = pp[0]  # row number
            reach_data.at[irech, 'j'] = pp[1]  # column number
            try:
                thk = self.mf.dis.thickness.array[:, int(pp[0]), int(pp[1])]
            except:
                xxx = 1
            if sum(thk) == 0:
                raise ValueError("Stream in inactive zone")
            for kk, val in enumerate(thk):
                if val > 0:
                    # reach_data.set_value(index, 'k', kk)
                    reach_data.at[irech, 'k'] = kk
                    break
            pass
            # IDs
            reach_data.at[irech, 'iseg'] = curr_seg_no  # Segment ID number
            reach_data.at[irech, 'ireach'] = 1  # Reach ID number

            # Stream topography
            reach_data.at[irech, 'rchlen'] = 300.0  # reach length
            row_mask = self.hru_param['HRU_ROW'] == pp[0] + 1
            col_mask = self.hru_param['HRU_COL'] == pp[1] + 1
            cell_info = self.hru_param[(row_mask & col_mask)]
            reach_data.at[irech, 'strtop'] = cell_info['DEM_ADJ'].values[0] - 1.0  # Streambed elevation is assumed 1
            # meter
            # below ground surface.
            reach_data.at[irech, 'slope'] = cell_info['DEM_SLP_P'].values[0] / 100.0  # Slope

            # Streambed information
            reach_data.at[irech, 'strthick'] = 0.5  # streambed thickness - meter
            reach_data.at[irech, 'strhc1'] = 0.0  # conductivity of the stream bed

            # Unsaturated Zone properties
            reach_data.at[irech, 'thts'] = 0.31  # saturated porosity
            reach_data.at[irech, 'thti'] = 0.131  # initial water content
            reach_data.at[irech, 'eps'] = 3.5  # Brooks-Corey exponent
            reach_data.at[irech, 'uhc'] = 0.1  # conductivity of the unsaturated zone

        return reach_data, segment_data

    def compute_ag_diversions2(self, segment_data_ss):
        """
        The difference between this function and the next one is that this calculates the ag diversion at the gages
        :param segment_data_ss:
        :return:
        """
        ag_farm = self.config.get('SFR', 'crop_hru')
        gage_hru_file = self.config.get('SFR', 'gage_file')
        field_hru = geopandas.read_file(ag_farm)
        gage_hru = geopandas.read_file(gage_hru_file)
        crop_water_requirements = {}
        crop_water_requirements['Mixed Pasture'] = 2.50
        crop_water_requirements['Grapes'] = 0.70
        crop_water_requirements['Apples'] = 1.5
        crop_water_requirements['Pears'] = 1.5

        crops_to_include = ['Apples', 'Grapes', 'Pears', 'Mixed Pasture']  # 98% of crops

        calulate_sfr_topo = True
        if calulate_sfr_topo:
            sfr_topo = {}
            for igage_rec, gage_rec in gage_hru.iterrows():
                seg = gage_rec['ISEG']
                up_segs = self.get_all_upstream_segs(seg)
                sfr_topo[seg] = np.array(up_segs)

            np.save('sfr_topo.npy', sfr_topo)
        else:
            sfr_topo = np.load('sfr_topo.npy', allow_pickle=True).all()

        # Now that the topology of the sfr is computed, let us
        # make sure that each gage has unique hrus
        for gage in sfr_topo.keys():
            curr_ups = sfr_topo[gage]
            for gag_ in sfr_topo.keys():
                if gag_ == gage:
                    continue
                ar2 = sfr_topo[gag_]
                curr_ups = np.setdiff1d(curr_ups, ar2)

            sfr_topo[gage] = curr_ups

        # compute diversions
        for gage in sfr_topo.keys():
            curr_fields = field_hru[field_hru['IRUNBOUND'].isin(sfr_topo[gage])]
            m2_to_acre = 0.000247105
            ac_ft_per_year_to_m3_per_day = 3.3794
            tot_demand = 0
            for crop in crop_water_requirements.keys():
                w_demand_per_acre = crop_water_requirements[crop]
                cropmask = curr_fields['Crop2014'] == crop
                area = curr_fields[cropmask]['Shape_Area'].sum()
                area_in_acre = area * m2_to_acre
                annual_deman_acre = w_demand_per_acre * area_in_acre
                daily_demand_m3 = annual_deman_acre * ac_ft_per_year_to_m3_per_day
                tot_demand = tot_demand - daily_demand_m3

            mask = segment_data_ss['nseg'] == gage
            segment_data_ss.loc[mask, 'flow'] = tot_demand

        return segment_data_ss

    def compute_ag_diversions(self, segment_data_ss):
        ag_farm = self.config.get('SFR', 'ag_farms_file')
        farms_df = pd.read_csv(ag_farm)
        crop_water_requirements = {}
        crop_water_requirements['Mixed Pasture'] = 2.50
        crop_water_requirements['Grapes'] = 0.70
        crop_water_requirements['Apples'] = 1.5
        crop_water_requirements['Pears'] = 1.5

        crops_to_include = ['Apples', 'Grapes', 'Pears', 'Mixed Pasture']  # 98% of crops
        for i, div_row in farms_df.iterrows():
            curr_seg = div_row['iseg']
            if curr_seg == 434:
                continue  # this is the outlet, no diversion
            flow = 0.0
            m2_to_acre = 0.000247105
            ac_ft_per_year_to_m3_per_day = 3.3794
            for crop in crop_water_requirements.keys():
                w_demand_per_acre = crop_water_requirements[crop]

                area_in_acre = div_row[crop] * 300.0 * 300.0 * m2_to_acre
                annual_deman_acre = area_in_acre * w_demand_per_acre
                daily_demand_m3 = annual_deman_acre * ac_ft_per_year_to_m3_per_day
                flow = flow + daily_demand_m3
            filter = segment_data_ss['nseg'] == curr_seg

            if segment_data_ss.loc[filter, 'iupseg'].values[0] <= 0:
                print('Error....')
            else:
                segment_data_ss.loc[filter, 'iprior'] = 0
                segment_data_ss.loc[filter, 'flow'] = flow

        return segment_data_ss

    def Steady_state_SFR_changes(self, segment_data, reach_data, average_inflows):
        """

        :param reach_data:
        :return:
        """
        # ---------------------
        # dam gate segment
        # --------------------
        gate_segs = self.config.get('SFR', 'gate_iseg')
        gate_segs = gate_segs.split(',')
        gate_segs = [int(ss) for ss in gate_segs]

        for sgate in gate_segs:
            locc = segment_data['nseg'] == sgate
            segment_data.loc[locc, 'flow'] = 1e-5

        # ---------------------
        # inflow segment
        # --------------------
        inflow_segs = self.config.get('SFR', 'inflow_segs')
        inflow_segs = inflow_segs.split(',')
        inflow_segs = [int(ss) for ss in inflow_segs]

        for ss in inflow_segs:
            locc = segment_data['nseg'] == ss
            segment_data.loc[locc, 'flow'] = average_inflows[ss]

        return segment_data, reach_data

    def spillway_calc(self, segment_data, reach_data):
        """

        :param segment_data:
        :param reach_data:
        :return:
        """
        # Spillways
        spillways_segs = self.config.get('SFR', 'spill_iseg')
        spillways_segs = spillways_segs.split(',')
        spillways_segs = [int(ss) for ss in spillways_segs]

        # also we need lakes info
        bathymetry_file = self.config.get('LAK', 'bathymetry_file')
        lake_df = pd.read_excel(bathymetry_file, sheet_name='Stage_range')

        for sspil in spillways_segs:
            locc = segment_data['nseg'] == sspil
            lake_id = segment_data.loc[locc, 'iupseg'].values[0] * -1
            if lake_id < 1:
                print("Error")
            upstage = lake_df[lake_df['Lake _ID'] == lake_id]['Stage up'].values
            dnstage = lake_df[lake_df['Lake _ID'] == lake_id]['Down'].values
            lake_stage = 0.5 * (upstage + dnstage)

            segment_data.loc[locc, 'icalc'] = 1
            segment_data.loc[locc, 'width1'] = 10
            segment_data.loc[locc, 'width2'] = 10

            # elevation is like outseg elevation
            dnseg = segment_data[segment_data['nseg'] == sspil]['outseg'].values[0]
            dn = segment_data[segment_data['nseg'] == dnseg]
            reach_dn = reach_data[(reach_data['iseg'] == dnseg) & (reach_data['ireach'] == 1)]
            spillway_elevation = 0.5 * (reach_dn['strtop'].values[0] + upstage)
            locc2 = reach_data['iseg'] == sspil

            reach_data.loc[locc2, 'rchlen'] = 400
            if reach_dn['strtop'].values[0] > spillway_elevation:
                xxxx = 1
            if spillway_elevation < (dnstage + 2.0):
                spillway_elevation = upstage - 2.0
            reach_data.loc[locc2, 'strtop'] = spillway_elevation
            reach_data.loc[locc2, 'slope'] = 0.1
            reach_data.loc[locc2, 'ireach'] = 1
            reach_data.loc[locc2, 'strhc1'] = 0.0

        return segment_data, reach_data

    def gates_calc(self, segment_data, reach_data, channel_flow_data):
        """
        dam gate segments. For gates segments, use outsegment geometry
        :param segment_data:
        :param reach_data:
        :param channel_flow_data:
        :return:
        """
        gate_segs = self.config.get('SFR', 'gate_iseg')
        gate_segs = gate_segs.split(',')
        gate_segs = [int(ss) for ss in gate_segs]
        # also we need lakes info
        bathymetry_file = self.config.get('LAK', 'bathymetry_file')
        lake_df = pd.read_excel(bathymetry_file, sheet_name='Stage_range')

        cfd = channel_flow_data[0].copy()
        for sgate in gate_segs:
            # get downstream segmet
            dnseg = segment_data[segment_data['nseg'] == sgate]['outseg'].values[0]
            dn = segment_data[segment_data['nseg'] == dnseg]
            reach_dn = reach_data[(reach_data['iseg'] == dnseg) & (reach_data['ireach'] == 1)]
            # dn is regular
            locc = segment_data['nseg'] == sgate
            lake_id = segment_data.loc[locc, 'iupseg'].values[0] * -1
            lake_stage = lake_df[lake_df['Lake _ID'] == lake_id]['Stage up'].values[0]

            segment_data.loc[locc, 'icalc'] = dn['icalc'].values[0]
            segment_data.loc[locc, 'width1'] = dn['width1'].values[0]
            segment_data.loc[locc, 'width2'] = dn['width2'].values[0]
            segment_data.loc[locc, 'nstrpts'] = dn['nstrpts'].values[0]
            locc2 = reach_data['iseg'] == sgate
            reach_data.loc[locc2, 'rchlen'] = reach_dn['rchlen'].values[0]

            # get the segment elevation
            if lake_id > 2:  # for small reservoir reach is 2 m above lakebed
                gate_elev = (lake_stage - 2.0)
            else:
                gate_elev = (lake_stage - 2.0)

            # find lake elevations
            locc_id = self.Lake_array == lake_id
            lake_bottom = self.mf.dis.botm.array[locc_id]

            # condition 1
            if reach_dn['strtop'].values[0] > gate_elev:
                print("Error, gate segment is below downstream next downstream segment")

            rch_length = 50.0
            slope = reach_dn['slope'].values[0]
            min_elevation = gate_elev - 0.5 * rch_length * slope

            # find which layer this elevation correpond to
            rrow = int(reach_data.loc[locc2, 'i'].values[0])
            rcol = int(reach_data.loc[locc2, 'j'].values[0])
            topp = self.mf.dis.top.array[rrow, rcol]
            elevs = [topp] + self.mf.dis.botm.array[:, rrow, rcol].tolist()

            for k in range(len(elevs) - 1):
                if min_elevation >= elevs[k]:
                    break
                if elevs[k] > min_elevation and elevs[k + 1] <= min_elevation:
                    break
            if lake_id > 2:
                reach_data.loc[locc2, 'k'] = k

            if k == self.mf.nlay - 1:
                if elevs[-1] > gate_elev:
                    botm = self.mf.dis.botm.array
                    botm[-1, rrow, rcol] = gate_elev - 2.0
                    self.mf.dis.botm = botm

            # -----
            reach_data.loc[locc2, 'strtop'] = gate_elev
            reach_data.loc[locc2, 'slope'] = reach_dn['slope'].values[0]
            reach_data.loc[locc2, 'ireach'] = 1
            reach_data.loc[locc2, 'strhc1'] = 0.0
            # check if the segment has irrigular cross-sec
            if dnseg in cfd.keys():
                # dn seg is irrigular shape
                cfd[sgate] = cfd[dnseg]
                dn['nstrpts'].values[0]
        cdf_2 = {}
        cdf_2[0] = cfd
        return segment_data, reach_data, cdf_2

    def compute_sfr_inflow(self):
        """

        :return:
        """

        fname = self.config.get('SFR', 'sfr_info_file')
        df = pd.read_excel(fname, sheet_name='info')
        tabfiles_dict = {}
        average_inflows = {}
        model_ws_tr = self.config.get('General_info', 'work_space')
        model_ws_tr = os.path.join(model_ws_tr, 'tr')
        for i, row in df.iterrows():
            sheetName = row['Inflow Name']
            iseg = row['ISEG']
            fn = row['Filename']
            inflow_data = pd.read_excel(fname, sheet_name=sheetName).values
            fn = os.path.join(model_ws_tr, fn)
            fid = open(fn, 'w')
            for rec in inflow_data:
                fid.write(str(rec[1]))
                fid.write(" ")
                flow = round(2446.58 * rec[2], 2)  # convert cfs to m3/day
                fid.write(str(flow))
                fid.write(" #")
                fid.write(str(rec[0].date()))
                fid.write("\n")
            fid.close()

            # average inflows for steady state model
            average_inflows[iseg] = np.mean(inflow_data[:, 2]) * 2446.58

            numval = len(inflow_data)
            iunit = self.mf.next_ext_unit()
            self.mf.external_units.append(iunit)
            self.mf.external_fnames.append(os.path.basename(fn))
            self.mf.external_binflag.append(0)
            tabfiles_dict[iseg] = {'numval': numval, 'inuit': iunit}
        return tabfiles_dict, average_inflows

    def sfr_cross_sections(self, reach_data, segment_data):
        def strictly_increasing(L):
            return all(x < y for x, y in zip(L, L[1:]))

        manning_n = float(self.config.get('SFR', 'mannings_roughness'))

        # get flow_data file
        flow_data = np.load(self.config.get('SFR', 'flow_date_file'), allow_pickle=True).all()
        channel_flow_data = {}
        curr_ch_flo_dt = {}
        for seg in flow_data.keys():
            # get slope of this seg
            curr_info = flow_data[seg]
            slp = reach_data[reach_data['iseg'] == seg]['slope'].values[0]
            previous_area = 0.0
            previous_wetted = 0.0
            previous_flow = 0.0
            q = []
            for index, row in curr_info.iterrows():
                darea = row['area'] - previous_area
                if darea <= 0:
                    pass
                dwetted = row['wetted'] - previous_wetted
                if dwetted <= 0:
                    pass
                dq = 86400 * (1.0 / manning_n) * darea * np.power(darea / dwetted, (2.0 / 3.0)) * \
                     np.power(slp, 0.5)
                q.append(previous_flow + dq)
                previous_area = previous_area + darea
                previous_wetted = previous_wetted + dwetted
                previous_flow = previous_flow + dq
            # q = (1.0/manning_n) * curr_info['area'] * np.power(curr_info[ 'hraduis'], (2.0/3.0)) * np.power(slp, 0.5)
            # q = q * 86400
            dpth = curr_info['max_depth'].values
            wdth = curr_info['width'].values
            if not strictly_increasing(wdth):
                pass
            if not strictly_increasing(q):
                pass
            curr_ch_flo_dt[seg] = [[0.0] + q, [0.0] + dpth.tolist(), [0.0] + wdth.tolist()]

            segment_data.loc[(segment_data['nseg'] == seg), ['icalc']] = 4
        channel_flow_data[0] = curr_ch_flo_dt

        ## rectangular sections
        return reach_data, segment_data, channel_flow_data

    def calculate_stream_slope(self, reach_data):
        min_slope = float(self.config.get('SFR', 'min_slope'))
        segs = reach_data['iseg'].unique()
        for iseg in segs:
            curr_seg = reach_data[reach_data['iseg'] == iseg]
            curr_seg = curr_seg.copy()
            curr_seg = curr_seg.sort_values(by=['ireach'])
            seg_len = curr_seg['rchlen'].sum() * 1.0
            slp = (curr_seg['strtop'].values[0] - curr_seg['strtop'].values[-1]) / seg_len
            if slp <= 0:
                slp = min_slope
            reach_data.loc[(reach_data['iseg'] == iseg), ['slope']] = slp
        return reach_data

    def cal_stream_width(self, streams_data, flow_acc_file):
        max_width = float(self.config.get('SFR', 'max_width'))
        min_width = float(self.config.get('SFR', 'min_width'))
        flow_acc_range = streams_data['flow_accum'].max() - streams_data['flow_accum'].min()
        widths = min_width + (max_width - min_width) * (
                streams_data['flow_accum'].values - streams_data['flow_accum'].min()) / flow_acc_range
        streams_data['Width'] = widths
        if False:
            streams_data.to_file('stream_width.shp')
        return streams_data

    def uzf_package(self):
        # option block
        from flopy.utils.optionblock import OptionBlock
        uzfstr = "specifythti\nspecifysurfk\nseepsurfk\n"
        uzfstr = ""
        nuztop = 2  # Recharge to and discharge from specified
        iuzfopt = 1  # 1 Vertical conductivity will specifed from UZF
        irunflg = 1  # >0 means water discharge will be routed to the streams.
        ietflg = 1  # > 0 ET will be simulated
        ipakcb = 55  # > 0 recharge, ET, and discharge will be written unformatted file
        iuzfcb2 = 0  # > 0  recharge, ET, and ground-water discharge to land surface rates to a separate
        ntrail2 = 15  # number of trailing waves
        nsets = 20  # number of wave sets used to simulate multiple infiltration periods

        # detailed information on the unsaturated zone water budget and water content.
        nuzgag = 1  # equal to the number of cells (one per vertical column) that will be specified for printing
        unit_num = -1 * self.mf.next_ext_unit()
        unit_nums = -1 * self.mfs.next_ext_unit()
        uzgage_tr = {unit_num: []}
        uzgage_ss = {unit_nums: []}

        surfdep = 1.0  # The average height of undulations, D (Figure 1 in UZF documentation), in the land surface altitude
        iuzfbnd = 1 + self.mf.nlay - np.sum(self.mf.bas6.ibound.array, axis=0)  # used to define the aerial extent of

        # active model in which recharge and discharge will be simulated.
        iuzfbnd[iuzfbnd > self.mf.nlay] = 0
        n_row = self.mf.nrow
        n_col = self.mf.ncol
        irunbnd = self.hru_param['IRUNBOUND'].values.reshape(n_row, n_col)

        # subbaasincs
        subbasins = self.hru_param['subbasin'].values.reshape(n_row, n_col)
        vks = np.zeros_like(self.mf.upw.hk.array[0, :, :])
        for k in range(self.mf.nlay):
            kh_layer = self.mf.upw.hk.array[k, :, :]
            mask = iuzfbnd == (k + 1)
            vks[mask] = kh_layer[mask]

        vks = vks * 0.0003  # Manual vks value (Rich)
        surfk = vks  # same zone [for Steady state only]
        eps = 4.0
        thts = self.hru_param['MOIST_MAX'].values.reshape(n_row, n_col)
        thts = 0.347 * thts / np.max(thts)
        thts = 0.35
        thti = 0.15
        pet = 9.500000E-05  # reasonable for riparian et
        extdp = 1.0
        extwc = 0.10
        annual_rain = 0.0
        for ii in np.arange(1, 13):
            # curr_ = np.copy(zmat)
            field_name = 'PPT_' + str(ii).zfill(2)
            annual_rain = annual_rain + self.hru_param[field_name].values.reshape(n_row, n_col)
        finf = 0.55 * (annual_rain / 365.25) / 1000.0  # convert units from mm/year to m/day
        finf = finf * self.mf.bas6.ibound.array[2, :, :]
        options = OptionBlock('', flopy.modflow.ModflowUzf1, block=True)
        options.specifythti = False
        options.seepsurfk = True
        options.specifysurfk = True
        options.rejectsurfk = False
        specifythti = False
        seepsurfk = True
        specifysurfk = True
        rejectsurfk = False
        # Todo: remove infiltration from transient model
        uzf = flopy.modflow.ModflowUzf1(self.mf, nuztop=nuztop, iuzfopt=iuzfopt, irunflg=irunflg, ietflg=ietflg,
                                        ipakcb=ipakcb, iuzfcb2=0, ntrail2=ntrail2, nsets=nsets, specifythti=
                                        specifythti, seepsurfk=seepsurfk, rejectsurfk=rejectsurfk,
                                        specifysurfk=specifysurfk, nuzgag=nuzgag, uzgag=uzgage_tr,
                                        surfdep=surfdep, iuzfbnd=iuzfbnd, irunbnd=irunbnd, vks=vks,
                                        eps=4.0, thts=thts, thti=thti, surfk=surfk, finf=finf, pet=pet,
                                        extdp=extdp,
                                        extwc=extwc, options=options)

        uzfs = flopy.modflow.ModflowUzf1(self.mfs, nuztop=nuztop, iuzfopt=iuzfopt, irunflg=irunflg, ietflg=ietflg,
                                         ipakcb=ipakcb, iuzfcb2=0, ntrail2=ntrail2, nsets=nsets, specifythti=
                                         specifythti, seepsurfk=seepsurfk, rejectsurfk=rejectsurfk,
                                         specifysurfk=specifysurfk, nuzgag=nuzgag, uzgag=uzgage_ss,
                                         surfdep=surfdep, iuzfbnd=iuzfbnd, irunbnd=irunbnd, vks=vks,
                                         eps=4.0, thts=thts, thti=thti, surfk=surfk, finf=finf, pet=pet,
                                         extdp=extdp,
                                         extwc=extwc, options=options)

    def rch_package(self):
        annual_rain = 0.0
        nrows = self.nrows
        ncols = self.ncols
        for ii in np.arange(1, 13):
            # curr_ = np.copy(zmat)
            field_name = 'PPT_' + str(ii).zfill(2)
            annual_rain = annual_rain + self.hru_param[field_name].values.reshape(nrows, ncols)
        annual_inf = 0.20 * (annual_rain / 365.25) / 1000.0  # convert units from mm/year to m/day
        finf = {}
        ipdx = 0
        for dt in range(self.mf.dis.nper):
            # yy = dt.year
            # mm = dt.month
            # dds = monthrange(yy, mm)
            # rech = rech_dict[dt.month] * 0.00328084 * 0.30 / dds[1]  # daily
            finf[ipdx] = np.copy(annual_inf)
            ipdx = ipdx + 1

        rch = flopy.modflow.ModflowRch(self.mf, rech=finf)

        pass

    def oc_package(self):
        # Add OC package to the MODFLOW model
        options = ['PRINT HEAD', 'PRINT DRAWDOWN', 'PRINT BUDGET',
                   'SAVE HEAD', 'SAVE DRAWDOWN', 'SAVE BUDGET',
                   'SAVE IBOUND', 'DDREFERENCE']
        idx = 0
        spd = dict()
        for sp in self.mf.dis.nstp.array:
            stress_period = idx
            step = sp - 1
            ke = (stress_period, step)
            idx = idx + 1
            spd[ke] = [options[3], options[2], options[5]]

        oc = flopy.modflow.ModflowOc(self.mf, stress_period_data=spd, cboufm='(20i5)')

        # Steady State
        spds = {}
        spds[(0, 0)] = [options[3], options[2], options[5]]
        oc = flopy.modflow.ModflowOc(self.mfs, stress_period_data=spds, cboufm='(20i5)')

    def add_rubber_dam_lak(self, nlakes):

        # TODO: double check that all I need to do is include the rubber dam lake in nlakes
        #  and that all the other code will work for the rubber dam as is

        # add rubber dam lake
        nlakes = nlakes + 1

        return nlakes


    def lak_package(self):

        # generate bathymetry files
        self.generate_bathymetry_files()
        self.generate_bathymetry_files_rubber_dam()

        # ------------- Record [1] --------------------
        options = ['TABLEINPUT']
        nlakes = self.hru_param['LAKE_ID'].max()
        ipakcb = 55  # this ILKCB

        # ------------- Make changes for rubber dam --------------------
        # TODO: check that this function should be self.function() rather than just function()
        nlakes = self.add_rubber_dam_lak(nlakes)

        # ------------- Record [2] --------------------
        theta = -0.8  # negative is a flag to read nssitr and sscncr when it is transeint.
        # For SS theta = 1
        # The following are used for transient simulation. They can be removed when theta is not negative.
        nssitr = 100  # Maximum number of iterations for Newton’s method of solution for equilibrium lake stages
        sscncr = 0.00001  # Convergence criterion for equilibrium lake stage solution
        surfdep = 0.1

        # ------------- Record [3] --------------------
        stages = []  # The initial stage of each lake at the beginning of the run
        stage_range = []  # this is needed only for SS simulation.
        rubber_dam_lake_id = int(self.config.get('RUBBER_DAM', 'rubber_dam_lake_id'))
        rubber_dam_stage_min = float(self.config.get('RUBBER_DAM', 'rubber_dam_min_lake_stage'))
        rubber_dam_stage_max = float(self.config.get('RUBBER_DAM', 'rubber_dam_max_lake_stage'))
        for lake_id in range(1, nlakes + 1, 1):
            lake_botm = []
            lake_top = []
            for k in range(self.mf.nlay):
                curr_lak_layer = self.Lake_array[k, :, :]
                id_loc = curr_lak_layer == lake_id
                if not np.any(id_loc):
                    continue
                if k == 0:
                    top2d = self.mf.dis.top.array
                    tops = max(top2d[id_loc])
                    botm2d = self.mf.dis.botm.array[k, :, :]
                    botms = min(botm2d[id_loc])
                    lake_botm.append(botms)
                    lake_top.append(tops)
                else:
                    botm2d = self.mf.dis.botm.array[k, :, :]
                    tops = max(botm2d[id_loc])
                    botms = min(botm2d[id_loc])
                    lake_botm.append(botms)
                    lake_top.append(tops)

            # update stage range
            if lake_id == rubber_dam_lake_id:
                stage_range.append((rubber_dam_stage_min, rubber_dam_stage_max))
            else:
                stage_range.append((min(lake_botm), max(lake_top)))
            ini_stage = (min(lake_botm) + max(lake_top)) * 0.5
            ini_stage = min(lake_botm)
            stages.append(ini_stage)


        tab_files = self.bathymetry_files  # TODO: Check if it is possible for flopy to choose unit numbers
        tab_units = None

        # ------------- Record [4] --------------------

        # ------------- Record [5] --------------------
        lakarr = self.Lake_array

        # ------------- Record [6] --------------------
        bdlknc = 0.1 + np.zeros_like(self.Lake_array)
        bdlknc[lakarr == 11] = 0

        # ------------- Record [7 and 8] --------------------
        # no sublacks

        # ------------- Record [9] --------------------
        # Fluxes
        flux_data = {}
        flux = []
        for id in range(nlakes):
            if id == 7:  # lake #8 is fussy
                flux.append([0.0, 0.0, 0.0, 0.0])
            else:
                flux.append([0.0, 0.025, 0.0, 0.0])  ##PRCPLK EVAPLK RNF WTHDRW [SSMN] [SSMX]
        flux_data[0] = flux

        # ------------- Create lake package --------------------
        lak = flopy.modflow.mflak.ModflowLak(self.mf, nlakes=nlakes, ipakcb=ipakcb, theta=theta, nssitr=nssitr,
                                             sscncr=sscncr,
                                             surfdep=surfdep, stages=stages, stage_range=stage_range,
                                             tab_files=tab_files,
                                             tab_units=tab_units, lakarr=lakarr,
                                             bdlknc=bdlknc, sill_data=None, flux_data=flux_data, extension='lak',
                                             unitnumber=None,
                                             filenames=None, options=options)

        laks = flopy.modflow.mflak.ModflowLak(self.mfs, nlakes=nlakes, ipakcb=ipakcb, theta=theta, nssitr=nssitr,
                                              sscncr=sscncr,
                                              surfdep=surfdep, stages=stages, stage_range=stage_range,
                                              tab_files=tab_files,
                                              tab_units=tab_units, lakarr=lakarr,
                                              bdlknc=bdlknc, sill_data=None, flux_data=flux_data, extension='lak',
                                              unitnumber=None,
                                              filenames=None, options=options)

    def generate_bathymetry_files(self):
        """

        :return:        """
        lake_elev_range = {}
        bathy_files_units = []
        lake_point_file = self.config.get('LAK', 'lake_point_file')
        bathymetry_file = self.config.get('LAK', 'bathymetry_file')
        elev_range = pd.read_excel(bathymetry_file, sheet_name='Stage_range')
        lak_shp = geopandas.read_file(lake_point_file)
        bathy_file_list = []
        nlakes = self.hru_param['LAKE_ID'].max()
        for lake_id in range(1, nlakes + 1, 1):
            name_root = elev_range[elev_range['Lake _ID'] == lake_id]['FileName'].values[0]
            # name_root = "LAKE_ID_" + str(lake_id) + ".dat"
            fn = os.path.join(self.mf.model_ws, name_root)
            parent_dir = os.path.abspath(os.path.join(self.mf.model_ws, os.pardir))
            wss = os.path.join(parent_dir, 'ss')
            fns = os.path.join(wss, name_root)
            if lake_id > 2:
                # this is a small lake
                # bed_elev = self.hru_param[self.hru_param['LAKE_ID'] == lake_id]['DEM_ADJ'].values[0]
                bed_elev = elev_range[elev_range['Lake _ID'] == lake_id]['Down'].values[0]
                curr_lake = lak_shp[lak_shp['LakeID'] == lake_id]
                normal_vol = curr_lake['NORMAL_STO'].values[0] * 1233.48
                surface_area = curr_lake['SURF_AREA'].values[0] * 4046.86
                dam_height = curr_lake['NID_HEIGHT'].values[0] * 0.3048
                # in this calculation we assume that the max dam height is the NID height,
                # Also we assume that the lake can be represented as inverted pyramid with square base
                width = surface_area ** 0.5  # square area
                maxH = (normal_vol * 3.0) / surface_area
                phi_angle = np.arctan(maxH * 2.0 / width)

                water_elev = np.linspace(0, maxH, 151)
                areas = ((2.0 * water_elev) / np.tan(phi_angle)) ** 2.0
                vols = areas * water_elev / 3.0
                curr_bathy = np.array([water_elev + bed_elev, vols, areas]).T
                top_elev = elev_range[elev_range['Lake _ID'] == lake_id]['Stage up'].values[0]
                lake_elev_range[lake_id] = [bed_elev, top_elev]

            else:
                # this is a major lake
                if lake_id == 1:
                    bathy = pd.read_excel(bathymetry_file, sheet_name='Mendo')
                elif lake_id == 2:
                    bathy = pd.read_excel(bathymetry_file, sheet_name='Sonoma')

                stage_elev = np.linspace(bathy['Stage'].values[0], bathy['Stage'].values[-1], 151)
                stage_elev = stage_elev
                f = interpolate.interp1d(bathy['Stage'], bathy['Volume'])
                vol = f(stage_elev).round(2)
                f = interpolate.interp1d(bathy['Stage'], bathy['Area'])
                area = f(stage_elev).round(2)
                stage_elev = stage_elev * 0.3048
                vol = vol * 1233.48
                area = area * 4046.86
                curr_bathy = np.array([stage_elev, vol, area]).T

            np.savetxt(fname=fn, X=curr_bathy, fmt='%6.2f')
            np.savetxt(fname=fns, X=curr_bathy, fmt='%6.2f')
            # iunit = self.mf.next_ext_unit()
            # bathy_files_units.append(iunit)
            # self.mf.external_units.append(iunit)
            # self.mf.external_fnames.append(os.path.basename(name_root))
            # self.mf.external_binflag.append(0)

            bathy_file_list.append(name_root)
        self.bathymetry_files = bathy_file_list
        self.lake_elev_range = lake_elev_range
        self.bathy_files_units = bathy_files_units

    def generate_bathymetry_files_rubber_dam(self):

        # create empty objects to store results
        lake_elev_range = self.lake_elev_range
        bathy_files_units = self.bathy_files_units
        bathy_file_list = self.bathymetry_files

        # specify rubber dam lake stage-volume-area relationship
        lake_id = int(self.config.get('RUBBER_DAM', 'rubber_dam_lake_id'))
        stage_min = float(self.config.get('RUBBER_DAM', 'rubber_dam_min_lake_stage'))
        stage_max = float(self.config.get('RUBBER_DAM', 'rubber_dam_max_lake_stage'))
        width_trapezoid_top = float(self.config.get('RUBBER_DAM', 'width_trapezoid_top'))
        width_trapezoid_base = float(self.config.get('RUBBER_DAM', 'width_trapezoid_base'))
        length_channel = float(self.config.get('RUBBER_DAM', 'length_channel'))
        height_max = stage_max - stage_min
        height_water = np.linspace(0, height_max, 151)
        width_trapezoid_water_surface = ((height_water / height_max) * width_trapezoid_top) + (
                    ((height_max - height_water) / height_max) * width_trapezoid_base)
        area_trapezoid = 0.5 * (width_trapezoid_base + width_trapezoid_water_surface) * height_water
        volume_trapezoidal_channel = area_trapezoid * length_channel
        stage_trapezoidal_channel = stage_min + height_water

        # store lake bathymetry data
        curr_bathy = np.array([stage_trapezoidal_channel, volume_trapezoidal_channel, area_trapezoid]).T
        lake_elev_range[lake_id] = [stage_min, stage_max]

        # prepare file path
        name_root = self.config.get('RUBBER_DAM', 'bathy_file_name_root')
        fn = os.path.join(self.mf.model_ws, name_root)
        parent_dir = os.path.abspath(os.path.join(self.mf.model_ws, os.pardir))
        wss = os.path.join(parent_dir, 'ss')
        fns = os.path.join(wss, name_root)

        # save results
        np.savetxt(fname=fn, X=curr_bathy, fmt='%6.2f')
        np.savetxt(fname=fns, X=curr_bathy, fmt='%6.2f')
        bathy_file_list.append(name_root)
        self.bathymetry_files = bathy_file_list
        self.lake_elev_range = lake_elev_range
        self.bathy_files_units = bathy_files_units

    def well_package(self):
        # Read flow rates files
        flow_rate_file = self.config.get('Wells', 'flowrate')  # acre_ft/month
        well_hru_file = self.config.get('Wells', 'wellhru')

        # Read shapefile for wells hru
        flow_rate = pd.read_csv(flow_rate_file)
        well_hru = geopandas.read_file(well_hru_file)
        well_hru.System = well_hru.System.values.astype(int)
        well_hru.loc[well_hru['Total_Dept'] == 'UNKNOWN', 'Total_Dept'] = 0
        well_hru.loc[well_hru['Total_Dept'] == '40+', 'Total_Dept'] = 40.0
        well_hru.loc[well_hru['Total_Dept'] == '40ft3in', 'Total_Dept'] = 40.0
        well_hru.loc[well_hru['Total_Dept'] == '40ft8in', 'Total_Dept'] = 40.0
        well_hru.loc[well_hru['Total_Dept'] == '60-65', 'Total_Dept'] = 65.0
        well_hru.loc[well_hru['Total_Dept'] == '60/80', 'Total_Dept'] = 70.0

        loc_wells_with_depth_info = np.logical_and(well_hru['Total_Dept'].values.astype(float) > 0,
                                                   well_hru['Perftop__f'].values.astype(float) > 0)
        wells_depth_info = well_hru[loc_wells_with_depth_info]

        # loop over water system in the flow_rate
        ws_ids = flow_rate['WS'].unique()
        all_wells_ss = []
        all_wells_tr = []
        for ws in ws_ids:
            curr_flow = flow_rate[flow_rate['WS'] == ws]
            curr_well_hrus = well_hru[well_hru['System'] == ws]
            n_wells = curr_well_hrus.shape[0]
            if n_wells == 0:
                continue  # no location

            # get row/col/layers and flow for the wells
            for i, well in curr_well_hrus.iterrows():
                row = well['HRU_ROW']  # modflow index
                col = well['HRU_COL']

                # get total depth
                try:
                    depth = well['Total_Dept'] * 0.3048  # ft to m
                except:
                    depth = np.NAN
                try:
                    perf_top = well['Perftop__f'] * 0.3048  # ft
                except:
                    perf_top = np.NAN
                if perf_top == 0: perf_top = np.NAN
                if depth == 0: depth = np.NAN
                # Try to fix the problem of depths issue
                if np.isnan(depth) & np.isnan(perf_top):
                    # No depth information is available, so we get the closest well with info
                    delx = np.power((wells_depth_info.HRU_COL.values - col), 2.0)
                    dely = np.power((wells_depth_info.HRU_ROW.values - row), 2.0)
                    dist_vec = np.power(delx + dely, 0.5)

                    close_well = wells_depth_info.iloc[np.argmin(dist_vec), :]

                    depth = float(close_well['Total_Dept']) * 0.3048
                    perf_top = float(close_well['Perftop__f']) * 0.3048
                    mid_point = (depth + perf_top) * 0.5
                elif np.isnan(depth) & (not np.isnan(perf_top)):
                    mid_point = perf_top
                elif (not np.isnan(depth)) & np.isnan(perf_top):
                    mid_point = depth
                else:
                    mid_point = (depth + perf_top) * 0.5

                # Now that the well depth is known find the layer  number
                botms = self.mf.dis.botm.array[:, row, col]
                top = self.mf.dis.top.array[row, col]
                mid_point = top - mid_point  # convert depth to elevation
                elevs = np.hstack((top, botms))
                ibound = self.mf.bas6.ibound.array[:, row, col]
                loc_top_active = np.where(np.cumsum(ibound) == 1)
                if len(loc_top_active[0]) == 0:
                    layer = 1
                else:
                    layer = loc_top_active[0][0] + 1

                for k in range(self.mf.dis.nlay):
                    if ibound[k] == 0:
                        continue
                    if elevs[k] > mid_point and elevs[k + 1] <= mid_point:
                        layer = k + 1  # the index here is modflow index
                        break

                # distribute pumping on wells
                acre_ft_to_cubic_meter = 1233.48
                flow = curr_flow['PumpingRate'].values
                years = curr_flow['Year'].astype(int).values
                months = curr_flow['Month'].astype(int).values
                days_in_month = [monthrange(yy_mm[0], yy_mm[1])[1] for yy_mm in zip(years, months)]
                flow = (flow / np.array(days_in_month)) * acre_ft_to_cubic_meter
                cols = np.ones_like(flow).astype(int) * int(col - 1)
                rows = np.ones_like(flow).astype(int) * int(row - 1)
                lays = np.ones_like(flow).astype(int) * int(layer - 1)
                stress_period = np.arange(0, len(months))
                loc = flow != 0
                curr_well = np.vstack((stress_period, lays, rows, cols, -flow, curr_flow['WS']))
                if len(all_wells_tr) == 0:
                    all_wells_tr = curr_well.T
                else:
                    all_wells_tr = np.vstack((all_wells_tr, curr_well.T))

                all_wells_ss.append([stress_period[0], lays[0], rows[0], -flow.mean(), ws])

        all_wells_tr = pd.DataFrame(all_wells_tr, columns=['SterssPeriod', 'k', 'i', 'j', 'flow', 'Name'])
        groups = all_wells_tr.groupby(['SterssPeriod'])
        well_dict = {}
        for group in groups:
            s_p = group[0]
            dat = group[1][['k', 'i', 'j', 'flow']]
            dat = dat.values.tolist()
            well_dict[s_p] = dat

        wel = flopy.modflow.mfwel.ModflowWel(self.mf, stress_period_data=well_dict)
        ccc = 1

    def well_package2(self):
        from flopy.utils.optionblock import OptionBlock

        options = OptionBlock('', flopy.modflow.ModflowWel, block=True)
        options.specify = True
        options.phiramp = 0.1
        options.iunitramp = self.mf.next_ext_unit()
        self.mf.external_fnames.append('pumping_reduction.out')
        self.mf.external_units.append(options.iunitramp)
        self.mf.external_binflag.append(0)

        well_file = self.config.get('Wells', 'WellFileReady')
        well_df = pd.read_csv(well_file)
        groups = well_df.groupby(['Stress_period'])
        well_dict = {}
        for group in groups:
            s_p = group[0] - 1
            dat = group[1][['Layer', 'Row', 'Col', 'Flow_Rate']]
            dat = dat.reset_index()
            dat['Layer'] = dat['Layer'].values - 1
            dat['Row'] = dat['Row'].values - 1
            dat['Col'] = dat['Col'].values - 1
            well_dict[s_p] = dat.values[:, 1:].tolist()

        wel = flopy.modflow.mfwel.ModflowWel(self.mf, ipakcb=55, stress_period_data=well_dict, options=options)

        # --------------------------
        # Steady state
        # --------------------------
        well_dict_ss = {}
        dat = well_df.groupby(['OBJECTID']).mean()
        dat = dat[['Layer', 'Row', 'Col', 'Flow_Rate']]
        dat = dat.reset_index()
        dat['Layer'] = dat['Layer'].values - 1
        dat['Row'] = dat['Row'].values - 1
        dat['Col'] = dat['Col'].values - 1
        well_dict_ss[0] = dat.values[:, 1:].tolist()
        options.iunitramp = self.mfs.next_ext_unit()
        self.mfs.external_fnames.append('pumping_reduction.wel.out')
        self.mfs.external_units.append(options.iunitramp)
        self.mfs.external_binflag.append(0)
        wels = flopy.modflow.mfwel.ModflowWel(self.mfs, ipakcb=55, stress_period_data=well_dict_ss, options=options)

        pass

    def correct_sfr2(self):
        if True:  # not needed any more
            # correct file
            fn = self.mf.sfr.fn_path
            ssfr = open(fn, 'r')
            content = ssfr.readlines()
            ssfr.close()
            content2 = []
            for line in content:
                if line.strip() == '':
                    pass
                else:
                    content2.append(line)
            ssfr = open(fn, 'w')
            for line in content2:
                ssfr.write(line)
            ssfr.close()

    def hfb_package(self):
        hfb_shp = self.config.get('Geo_Framework', 'hfb_file')
        hfb_att = geopandas.read_file(hfb_shp)
        nphfb = 0  # Number of horizontal-flow barrier parameters
        mxfb = 0  # Maximum number of horizontal-flow barrier barriers that will be defined using parameters (
        # Number of horizontal-flow barriers not defined by parameters. This is calculated automatically by FloPy based on the information in layer_row_column_data (default is 0).

        hfb_data = []
        hydchr = 10
        curr_hfb = []
        for i in np.arange(len(hfb_att)):

            for layer in np.arange(0, self.mf.nlay):
                curr_hfb.append(layer)
                curr_hfb.append(hfb_att.loc[i]['ROWVAL_1'])
                curr_hfb.append(hfb_att.loc[i]['COLVAL_1'])
                curr_hfb.append(hfb_att.loc[i]['ROWVAL_2'])
                curr_hfb.append(hfb_att.loc[i]['COLVAL_2'])
                curr_hfb.append(hydchr)
                hfb_data.append(curr_hfb)
                curr_hfb = []

        nhfbnp = len(hfb_data)
        nacthfb = len(hfb_data)
        # unit = self.mf.get_free_unit()
        hfb = flopy.modflow.ModflowHfb(self.mf, nphfb=nphfb, mxfb=mxfb, nhfbnp=nhfbnp, hfb_data=hfb_data,
                                       nacthfb=nacthfb,
                                       no_print=False, options=None)
        hfb = flopy.modflow.ModflowHfb(self.mfs, nphfb=nphfb, mxfb=mxfb, nhfbnp=nhfbnp, hfb_data=hfb_data,
                                       nacthfb=nacthfb,
                                       no_print=False, options=None)
        pass
        pass

    def hob_package(self):
        Build_HOB_FLG = int(self.config.get('HOB', 'Build_hob'))
        if Build_HOB_FLG:
            hob_file = self.config.get('HOB', 'hob_file')
            hob_df = geopandas.read_file(hob_file)
            hob_df = hob_df.dropna(subset=['WL_Date'])
            hob_df['WL_Date'] = pd.to_datetime(hob_df['WL_Date'])
            well_ids = hob_df['well_ID'].unique()

            hoblist = []
            hoblist_ss = []
            counter = -1
            all_info = []
            for ii, well in enumerate(well_ids):
                curr_well = hob_df[hob_df['well_ID'] == well]
                curr_well = curr_well.copy()
                curr_well = curr_well[curr_well['wl_elev_ft'] != -9999]
                if curr_well.empty:
                    continue
                curr_well = curr_well.reset_index()

                # get coordinates
                xo = curr_well['POINT_X'].values[0]
                yo = curr_well['POINT_Y'].values[0]
                xc = curr_well['HRU_X'].values[0]
                yc = curr_well['HRU_Y'].values[0]
                roff = -(yo - yc) / 300.0
                coff = (xo - xc) / 300.0

                # coordinates
                c_row = int(curr_well['HRU_ROW'].values[0] - 1)
                c_col = int(curr_well['HRU_COL'].values[0] - 1)

                # assume that per_top and pef_botm are depths not elevations
                perf_top = curr_well['top_ft'].values[0] * 0.3048
                perf_botm = curr_well['bot_ft'].values[0] * 0.3048
                if perf_botm > 0 or perf_top > 0:
                    if perf_botm > 0 and perf_top > 0:
                        well_depth = 0.5 * (perf_top + perf_botm)
                    else:
                        well_depth = perf_top + perf_botm
                else:
                    well_depth = 0.0  # no information

                top1 = self.mf.dis.top.array[c_row, c_col]
                curr_depth = top1 - well_depth
                bot2 = self.mf.dis.botm[:, c_row, c_col]
                elev = np.hstack((top1, bot2))
                ibound = self.mf.bas6.ibound.array[:, c_row, c_col]
                if sum(ibound) == 0:
                    continue
                if well_depth == 0:
                    # no data about depth is available, assign the well to the top active layer
                    for kk, ib in enumerate(ibound):
                        nly_n = kk
                        if ib > 0:
                            break
                else:
                    # assign depth a
                    for ie in np.arange(self.mf.nlay):  # [top,...., bot]
                        if ie < self.mf.nlay - 1:
                            if curr_depth <= elev[ie] and curr_depth > elev[ie + 1]:
                                nly_n = ie
                                break
                        else:
                            nly_n = ie

                # get observation time
                hds = curr_well['wl_elev_ft'].values * 0.3048
                dates = curr_well.WL_Date.values

                sim_start_date = datetime.datetime(year=1989, month=12, day=31)
                sim_end_date = datetime.datetime(year=2015, month=12, day=31)
                End_time = (sim_end_date - sim_start_date).days
                days = dates - np.datetime64(sim_start_date)
                days = days.astype('timedelta64[D]')
                days = days / np.timedelta64(1, 'D')

                time_mask = np.logical_and(days > 0, days < End_time)
                hds = hds[time_mask]
                days = days[time_mask]

                if len(days) == 0:
                    continue

                tim_ser_data = np.vstack((days, hds))
                tim_ser_data = tim_ser_data.transpose()
                counter = counter + 1
                obsname = 'HO_' + str(counter)
                print(obsname)
                cc_well_info = [obsname, well, len(hds), np.min(hds), np.max(hds), np.mean(hds), np.std(hds),
                                np.median(hds), elev[0], elev[-1], nly_n, c_row, c_col]
                all_info.append(cc_well_info)
                obs_tr = flopy.modflow.HeadObservation(self.mf, obsname=obsname, layer=nly_n, row=c_row,
                                                       column=c_col, roff=roff, coff=coff, itt=1,
                                                       time_series_data=tim_ser_data)

                # steady state
                tim_ser_data2 = [[0.0, np.mean(hds)]]
                obs_ss = flopy.modflow.HeadObservation(self.mf, obsname=obsname, layer=nly_n, row=c_row,
                                                       column=c_col, roff=roff, coff=coff, itt=1,
                                                       time_series_data=tim_ser_data2)
                hoblist.append(obs_tr)
                hoblist_ss.append(obs_ss)

        if Build_HOB_FLG:
            hobss = {}
            hobss['ss'] = hoblist_ss
            hobss['tr'] = hoblist
            np.save('rr_hob.npy', hobss)
        else:
            all_hobs = np.load('rr_hob.npy', allow_pickle=True)
            all_hobs = all_hobs.all()
            hoblist = all_hobs['tr']
            hoblist_ss = all_hobs['ss']

        hob_tr = flopy.modflow.ModflowHob(self.mf, hobdry=-9999., obs_data=hoblist, iuhobsv=self.mf.next_ext_unit())
        hob_ss = flopy.modflow.ModflowHob(self.mfs, hobdry=-9999., obs_data=hoblist_ss, iuhobsv=
        self.mfs.next_ext_unit())
        if Build_HOB_FLG:
            obs_info = pd.DataFrame(all_info, columns=['obsname', 'well_id', 'num_meas', 'min', 'max', 'mean', 'std',
                                                       'median', 'grid_top_elev', 'grid_bot_elev', 'layer', 'row',
                                                       'col'])
            obs_info.to_csv('rr_obs_info.csv')

        pass

    def gage_package(self):
        gage_file = self.config.get('SFR', 'gage_file')
        gage_df = geopandas.read_file(gage_file)
        gage_data = []

        files = []
        for id, row in gage_df.iterrows():
            seg = row['ISEG']
            irch = row['IREACH']
            gage_name = row['Gage_Name']
            unit = self.mf.next_ext_unit()
            unit2 = self.mfs.next_ext_unit()
            fname = gage_name + '.go'
            gauge = [seg, irch, unit, 1]
            gage_data.append(gauge)
            files.append(fname)
        # for mendo lak
        unit = self.mf.next_ext_unit()
        unit2 = self.mfs.next_ext_unit()
        gauge = [-1, -1 * unit, 3]
        gage_data.append(gauge)
        files.append("mendo_lake_bdg.lak.out")

        # for sonoma lak
        unit = self.mf.next_ext_unit()
        unit2 = self.mfs.next_ext_unit()
        gauge = [-2, -1 * unit, 3]
        gage_data.append(gauge)
        files.append("sonoma_lake_bdg.lak.out")

        num_gages = gage_df.values.shape[0] + 2  # two for the two lakes
        gage = flopy.modflow.ModflowGage(self.mf, numgage=num_gages, gage_data=gage_data, files=files)
        gages = flopy.modflow.ModflowGage(self.mfs, numgage=num_gages, gage_data=gage_data, files=files)

        pass

    def get_all_upstream_segs(self, seg):
        sfr = self.hru_param[self.hru_param['ISEG'] > 0]
        curr_seg = seg
        wait_list = []
        up_seg_for_this_div = []
        while True:
            up_seg_for_this_div.append(curr_seg)
            current_up = self.get_next_up(sfr, curr_seg)

            if len(current_up) == 0:
                if len(wait_list) > 0:
                    current_up = wait_list[0]
                    wait_list.pop(0)
                else:
                    # print("Segm {} Done!".format(seg))
                    break
            else:
                if len(current_up) > 0:
                    wait_list = wait_list + current_up[1:]
                    current_up = current_up[0]

            curr_seg = current_up

        # check for all diversions
        divv = sfr[sfr['IUPSEG'] > 0]
        for ic, rr in divv.iterrows():
            if rr['IUPSEG'] in up_seg_for_this_div:
                up_seg_for_this_div.append(rr['ISEG'])

        return np.unique(up_seg_for_this_div).tolist()

    def get_next_up(self, sfr, iseg):
        upseg = sfr[sfr['OUTSEG'] == iseg]['ISEG']
        upseg = upseg.unique().tolist()
        iupseg = sfr[sfr['ISEG'] == iseg]['IUPSEG']
        iupseg = iupseg.unique().tolist()

        # extr outseg above the lake
        for lakeid in iupseg:
            if lakeid < 0:
                upplake = sfr[sfr['OUTSEG'] == lakeid]['ISEG']
                upseg = upseg + upplake.unique().tolist()

        if len(iupseg) > 0:
            if iupseg[0] != 0:
                upseg = upseg + iupseg

        return upseg

    def ghb_package(self):
        ghb_hru_file = self.config.get('GHB', 'hru_ghb_file')
        ghb_df = geopandas.read_file(ghb_hru_file)
        groups = ghb_df.groupby('ghh_id')
        cond = 40000  # like Santa Rosa model
        ghb_data = []
        for ghb_section in groups:
            for icell, cell in ghb_section[1].iterrows():
                row = cell['HRU_ROW'] - 1
                col = cell['HRU_COL'] - 1

                ib_ghb = self.mf.bas6.ibound.array[:, row, col]
                head = self.mf.bas6.strt.array[:, row, col]
                head[ib_ghb == 0] = np.nan
                head = np.nanmean(head)
                for lay, ib in enumerate(ib_ghb):
                    if ib == 0:
                        continue
                    botm = self.mf.dis.botm.array[lay, row, col]
                    if (head - botm) < 2.0:
                        head = botm + 2.0
                    ghb_data.append([lay, row, col, head, cond])
        ghb_stress_per = {}
        ghb_stress_per[0] = ghb_data
        ipakcb = 55
        ghb = flopy.modflow.mfghb.ModflowGhb(self.mf, ipakcb=ipakcb, stress_period_data=ghb_stress_per, dtype=None,
                                             no_print=False,
                                             options=None, extension='ghb')
        ghbs = flopy.modflow.mfghb.ModflowGhb(self.mfs, ipakcb=ipakcb, stress_period_data=ghb_stress_per, dtype=None,
                                              no_print=False,
                                              options=None, extension='ghb')

    pass
