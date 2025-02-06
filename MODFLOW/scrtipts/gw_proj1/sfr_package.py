"""
Disclaimer: This information is preliminary and is subject to revision. It is being provided to meet the need for
timely best science. The information is provided on the condition that neither the U.S. Geological Survey nor the U.S.
Government shall be held liable for any damages resulting from the authorized or unauthorized use of the information.
"""
import sys, os
import flopy
import numpy as np
import pandas as pd
import logging

# optional package
try:
    import geopandas as gpd
    use_geopandas = True
except:
    use_geopandas = False


###############################################
def entry():
    print("---- SFR Package Generation-----\n")
    print("---- Version 1.1\n")

    if len(sys.argv)>1:
        print("- Reading excel supplied from the command window.....\n")
        print("- File name is {}".format(sys.argv[1]))
        sfr_info = sys.argv[1]
    else:
        print("- No information file is supplied. It is assumed that file exists locally and has the name "
              "sfr_info.xlsx\n")
        sfr_info = os.path.join(os.getcwd(), r"sfr_info.xslsx\n")

    sfr = Stream(sfr_info=sfr_info)


class Stream():
    def __init__(self, sfr_info = None):

        self.sfr_info = sfr_info

        # Check if the sfr_info is a correct file
        if not os.path.isfile(sfr_info):
            raise ValueError('{} is not a valid file...'.format(str(sfr_info)))

        # Satrt working on package generation
        self.generate_sfr()

    def generate_sfr(self):
        """

        :return:
        """
        #1) Read excel file for info
        print("---- Reading Excel info file .........\n")
        self.read_info()
        print("---- Finish reading info file ........\n")


        #2) Setup the SFR package
        self.sfr_setup()

        #3) Write SFR file


        pass
    def _reach_data(self):
        """
        Will use hru shape file to produce read data, next it will try to
        overwrite if self.rech_info has different data
        :return:
        """
        rows = self.hru_df['HRU_ROW'] - 1
        cols = self.hru_df['HRU_COL'] - 1
        #self.top = self.hru_df['DEM_MEAN'].values - self.streambed_depths

        reach_data_labels = ['node', 'k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope', 'strthick', 'strhc1',
                             'thts','thti', 'eps', 'uhc', 'reachID', 'outreach']
        streem_info_loc = self.hru_df['ISEG'] > 0
        rch_df = pd.DataFrame(columns=reach_data_labels, dtype='float')
        rch_df['k'] = self.hru_df.loc[streem_info_loc]['KRCH'] - 1
        rch_df['i'] = self.hru_df.loc[streem_info_loc]['IRCH'] - 1
        rch_df['j'] = self.hru_df.loc[streem_info_loc]['JRCH'] - 1

        # make sure that the stream exist in the top active layer
        if self.mf:
            kk = rch_df['k'].values.astype(int)
            ii = rch_df['i'].values.astype(int)
            jj = rch_df['j'].values.astype(int)
            for n, k_val in enumerate(kk):
                thk = self.mf.dis.thickness.array[:, ii[n], jj[n]]
                for ival, val in enumerate(thk):
                    if val>0:
                        break
                kk[n] = ival
        rch_df['k'] = kk
        rch_df['iseg'] = self.hru_df.loc[streem_info_loc]['ISEG']
        rch_df['ireach'] = self.hru_df.loc[streem_info_loc]['IREACH']
        rch_df['rchlen'] = self.hru_df.loc[streem_info_loc]['RCHLEN']
        rch_df['strtop'] = self.hru_df.loc[streem_info_loc]['DEM_MEAN'] - self.streambed_depth

        # check for errors in strtop elevations
        str_elv = rch_df['strtop'].values
        for n, k_val in enumerate(kk):
            elv = self.mf.dis.botm.array[kk[n], ii[n], jj[n]]
            if elv > str_elv[n]:
                str_elv[n] = elv + 1e-3
        rch_df['strtop'] = str_elv
        # now use excel data in self.rech_info
        no_more_stars = False
        for index, row_record in self.rech_info.iterrows():
            if row_record['iseg'] == '*' and no_more_stars == False:
                no_more_stars = True # this will prevent reading more lines with iseg=='*'
                rch_df['slope'] = row_record['slope']
                rch_df['strthick'] = row_record['strthick']
                rch_df['strhc1'] = row_record['strhc1']
                rch_df['thts'] = row_record['thts']
                rch_df['thti'] = row_record['thti']
                rch_df['eps'] = row_record['eps']
                rch_df['uhc'] = row_record['uhc']
            else:
                # find the segment number and reach number to overwrite the default
                mask1 = rch_df['iseg']== row_record['iseg']
                mask2 = rch_df['ireach']== row_record['ireach']
                mask = np.logical_and(mask1, mask2)
                for label in row_record.index:
                    if not (row_record[label]== '*'):
                        rch_df[label] = rch_df[label].mask(mask, row_record[label])
        self.rch_df = rch_df.reset_index()
        self.nstrm = len(rch_df) # number of reaches
        self.nss = rch_df['iseg'].values.max()

    def _segment_data(self):

        # Segment Data Structure
        seg_data_labels = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior',
                           'nstrpts', 'flow', 'runoff', 'etsw', 'pptsw', 'roughch', 'roughbk',
                           'cdpth', 'fdpth', 'awdth', 'bwdth', 'hcond1', 'thickm1',
                           'elevup', 'width1', 'depth1', 'hcond2', 'thickm2', 'elevdn',
                           'width2', 'depth2']
        zero_data = np.zeros((self.nss, len(seg_data_labels)))
        seg_df= pd.DataFrame(zero_data, columns=seg_data_labels, dtype='float')
        seg_df['nseg'] = np.arange(1, self.nss + 1)
        outseg = []
        iupseg = []
        for seg in np.arange(1, self.nss + 1):
            loc = self.hru_df['ISEG'] == seg
            outseg.append(self.hru_df.loc[loc]['OUTSEG'].values[0])
            iupseg.append(self.hru_df.loc[loc]['IUPSEG'].values[0])

        seg_df['outseg'] = outseg
        seg_df['iupseg'] = iupseg
        no_more_stars = False
        for index, row_record in self.seg_info.iterrows():
            if row_record['nseg'] == '*' and no_more_stars == False: # this will set the default values
                no_more_stars = True  # this will prevent reading more lines with iseg=='*'
                for label in row_record.index:
                    if row_record[label] != '*':
                        seg_df[label] = row_record[label]
            else:
                # find the segment number and reach number to overwrite the default
                mask = seg_df['nseg'] == row_record['nseg']
                for label in row_record.index:
                    if not (row_record[label] == '*'):
                        seg_df[label] = seg_df[label].mask(mask, row_record[label])
        pass







    def sfr_setup(self):

        self._reach_data()
        self._segment_data()


        pass
    def _read_main_info(self):
        """

        :return:
        """
        self.info = pd.read_excel(self.sfr_info, sheet_name='Info', skiprows=1)
        self.info = self.info.set_index('Parameter Name')
        self.mf_name = self.info.get_value(index='MODFLOW Name File', col='Value')
        self.hru_param_shp_file = self.info.get_value(index='HRU_PARAM shapefile', col='Value')
        self.hru_param_csv_file = self.info.get_value(index='HRU_PARAM CSV file', col='Value')
        self.sfr_file = self.info.get_value(index='sfr file name', col='Value')
        self.len_unit = self.info.get_value(index='Length Unit', col='Value')
        self.time_unit = self.info.get_value(index='Time Unit', col='Value')
        self.streambed_depth = self.info.get_value(index='Streambed depth below surface', col='Value')
        self.cellsize =  self.info.get_value(index='Cell Size', col='Value')

    def _read_sgm_rech_info(self):
        """

        :return:
        """
        self.seg_info = pd.read_excel(self.sfr_info, sheet_name='Segments Info', skiprows=7)
        self.rech_info = pd.read_excel(self.sfr_info, sheet_name='Reaches Info', skiprows=7)
        pass

    def read_info(self):
        # check if the file is excel file
        if not (self.sfr_info.split(".")[-1] in ['xls', 'xlsx']):
            raise ValueError("The extension of file {} does not seems to be for excel".format(self.sfr_info))

        # read Model Info
        self._read_main_info()

        # read Segment info
        self._read_sgm_rech_info()

        # read_modflow
        self.mf = None
        if os.path.isfile(self.mf_name):
            try:
                self.mf = flopy.modflow.Modflow.load(self.mf_name, load_only=['DIS', 'BAS6'])
            except:
                raise ValueError(" Cannot read model file {}".format(self.mf_name))

        # read hru_param
        try:
            print("Reading HRU_PARAM shapefile ...")
            self.hru_df = gpd.read_file(self.hru_param_shp_file)
        except:
            print("Cannot read shapefile {}. Try to read csv file....".format(self.hru_param_shp_file))
            try:
                print("Reading HRU_PARAM csv file ...")
                self.hru_df = pd.read_csv(self.hru_param_csv_file)
            except:
                raise ValueError("Cannot read shapefile {}".format(self.hru_param_csv_file))






##############################################

def main():
    stream = Stream_package()
    ##-------------- Parameters to Change --------------------------------------
    stream.nlyars = 1
    stream.botm = 0  # arrays of layers bottom elevations
    stream.nper = 10  # number of stress period
    stream.perlen = 10  # for each stress period provide the its length
    stream.nstp = 10  # number of time steps in each stress period
    stream.depth_below_groundsurface = 0.3 # meter
    ##----------------------------------------------------------------------------

    rows = stream.att_table['HRU_ROW'] - 1
    cols = stream.att_table['HRU_COL'] - 1
    stream.nrows = np.max(stream.att_table['HRU_ROW'])
    stream.ncols = np.max(stream.att_table['HRU_COL'])
    mask1 = stream.att_table['HRU_COL'].values == 1
    mask2 = stream.att_table['HRU_COL'].values == 2
    delx = stream.att_table['HRU_X'].values[mask2] - stream.att_table['HRU_X'].values[mask1]
    stream.cellsize = delx[0]
    stream.top = stream.att_table['DEM_MEAN'].values - stream.depth_below_groundsurface  # an array of ground-surface elevation

    top = np.ones((stream.nrows, stream.ncols), dtype=np.float32)
    top[rows, cols] = stream.top
    stream.top = top

    att_table = stream.att_table

    # get reach data
    reach_data_labels = ['node', 'k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope', 'strthick', 'strhc1', 'thts',
                         'thti', 'eps', 'uhc', 'reachID', 'outreach']
    streem_info_loc = att_table['ISEG'] > 0
    df_stream = pd.DataFrame(columns=reach_data_labels, dtype='float')
    df_stream['k'] = att_table.loc[streem_info_loc]['KRCH'] - 1
    df_stream['i'] = att_table.loc[streem_info_loc]['IRCH'] - 1
    df_stream['j'] = att_table.loc[streem_info_loc]['JRCH'] - 1
    df_stream['iseg'] = att_table.loc[streem_info_loc]['ISEG']
    df_stream['ireach'] = att_table.loc[streem_info_loc]['IREACH']
    df_stream['rchlen'] = att_table.loc[streem_info_loc]['RCHLEN']
    df_stream['strtop'] = att_table.loc[streem_info_loc]['DEM_ADJ'] - stream.depth_below_groundsurface

    ##-------------- Parameters to Change --------------------------------------
    df_stream['slope'] = 0.001
    df_stream['strthick'] = 0.3  #
    df_stream['strhc1'] = 0.1
    df_stream['thts'] = 0.35
    df_stream['thti'] = 0.35
    df_stream['eps'] = 3.5
    df_stream['uhc'] = 0.1
    ##----------------------------------------------------------------------------

    reach_data = df_stream.to_records()
    reach_data = stream.remove_field_num(reach_data, 0)  # remove first column
    stream.nstrm = len(reach_data)  # number of reaches

    # Segment Data Structure
    seg_data_labels = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior',
                       'nstrpts', 'flow', 'runoff', 'etsw', 'pptsw', 'roughch', 'roughbk',
                       'cdpth', 'fdpth', 'awdth', 'bwdth', 'hcond1', 'thickm1',
                       'elevup', 'width1', 'depth1', 'hcond2', 'thickm2', 'elevdn',
                       'width2', 'depth2']

    zero_data = np.zeros((stream.nss, len(seg_data_labels)))
    df_seg_stream = pd.DataFrame(zero_data, columns=seg_data_labels, dtype='float')
    outseg = []
    iupseg = []
    for seg in np.arange(1, stream.nss + 1):
        loc = att_table['ISEG'] == seg
        outseg.append(att_table.loc[loc]['OUTSEG'].values[0] )
        iupseg.append(att_table.loc[loc]['IUPSEG'].values[0])

    df_seg_stream['nseg'] = np.arange(1, stream.nss + 1)
    df_seg_stream['icalc'] = stream.icalc
    df_seg_stream['outseg'] = outseg
    df_seg_stream['iupseg'] = iupseg
    df_seg_stream['nstrpts'] = stream.nstrpts  #
    df_seg_stream['flow'] = stream.flow
    df_seg_stream['roughch'] = stream.roughch
    df_seg_stream['roughbk'] = stream.roughbk
    df_seg_stream['cdpth'] = stream.cdpth
    df_seg_stream['fdpth'] = stream.fdpth
    df_seg_stream['awdth'] = stream.awdth
    df_seg_stream['bwdth'] = stream.bwdth
    # up
    df_seg_stream['hcond1'] = stream.hcond1
    df_seg_stream['thickm1'] = stream.thickm1
    df_seg_stream['elevup'] = stream.stream_up_elv

    df_seg_stream['width1'] = stream.width1
    df_seg_stream['depth1'] = stream.depth1
    # down
    df_seg_stream['hcond2'] = stream.hcond2
    df_seg_stream['thickm2'] = stream.thickm2
    df_seg_stream['elevdn'] = stream.stream_down_elv
    df_seg_stream['width2'] = stream.width2
    df_seg_stream['depth2'] = stream.depth2

    ss_segment_data = df_seg_stream.to_records()
    ss_segment_data = stream.remove_field_num(ss_segment_data, 0)
    segment_data = {0: ss_segment_data}

    # channel flow data
    channel_flow_data = {}  # for 6e - flow table [flow1 flow2; depth1, depth2, width1, width2]
    channel_geometry_data = {}  # 6d - complex channel cross-section
    nstrm = len(reach_data)  # number of reaches
    nss = len(segment_data[0])  # number of segments
    nsfrpar = 0  # number of parameters (not supported)
    nparseg = 0
    const =  86400  # constant for manning's equation, units of m/day
    dleak = 0.0001  # closure tolerance for stream stage computation
    ipakcb = 53  # flag for writing SFR output to cell-by-cell budget (on unit 53)
    istcb2 = 81  # flag for writing SFR output to text file
    nstrail = 10  # used when USZ is simulated, number of trailing wave increments
    isuzn = 1  # used when USZ is simulated, number of vertical cells in unz, for icalc=1, isuzn = 1
    nsfrsets = 30  # used when USZ is simulated, number of sets of trailing wave
    irtflg = 0  # an integer value that flags whether transient streamflow routing is active
    numtim = 2  # used when irtflg > 0, number of sub time steps to route streamflow
    weight = 0.75  # used when irtflg > 0,A real number equal to the time weighting factor used to calculate the change in channel storage.
    #  flwtol = 0.0001  # is a default value
    dataset_5 = {}
    for i in np.arange(stream.nper):
        if i == 0:
            tss_par = nss
        else:
            tss_par = -1
        dataset_5[i] = [tss_par, 0, 0]

    stream.model()
    sfr = flopy.modflow.ModflowSfr2(stream.mf, nstrm=nstrm, nss=nss, const=const, nsfrpar=nsfrpar, nparseg=nparseg,
                                    dleak=dleak, ipakcb=ipakcb, nstrail=nstrail, isuzn=isuzn, nsfrsets=nsfrsets,
                                    istcb2=istcb2, reachinput=True, isfropt=stream.isfropt, irtflg=irtflg,
                                    reach_data=reach_data, numtim=numtim, weight=weight,
                                    segment_data=segment_data,
                                    channel_geometry_data=channel_geometry_data,
                                    channel_flow_data=channel_flow_data,
                                    dataset_5=dataset_5)

    sfr.write_file("sfr_file.sfr")


class Stream_package(object):
    def __init__(self):
        self.shp_file = os.path.join(os.getcwd(), r"hru_param.csv")
        att_table = pd.read_csv(self.shp_file )
        self.att_table = att_table
        ##-------------- Parameters to Change --------------------------------------
        # provide information for each segment, here we use constant value just as place holder
        self.icalc = 1
        self.nstrpts = 0
        self.flow = 0  # flow entering or leaving each segment
        self.roughch = 0.03  # Manning's roughnes used for icalc = 1, and 2
        self.roughbk = 0.045  # Manning's roughness coefficient for the overbank areas (icalc = 2)
        self.cdpth = 0.3  # (DEPTH = CDPTH x Q^FDPTH) for icalc = 3
        self.fdpth = 0.35  # (DEPTH = CDPTH x Q^FDPTH) for icalc = 3
        self.awdth = 3.80  # WIDTH = AWDTH  x Q^BWDTH for icalc = 3
        self.bwdth = 0.6  # WIDTH = AWDTH x Q^BWDTH for icalc = 3
        self.hcond1 = 3.00E-05  # Hydraulic conductivity of the streambed at the upstream end of
        self.isfropt = 3  #
        self.thickm1 = 0.3  # Thickness of streambed material
        self.extract_stream_elev(att_table)
        self.width1 = 3.0
        self.depth1 = 0.6
        self.hcond2 = 3.00E-05
        self.thickm2 = 0.3
        self.width2 = 3.0
        self.depth2 = 0.6
        # ---------------------------------------------------------------------------------

    def extract_stream_elev(self, att_table):
        streem_info_loc = att_table['ISEG'] > 0
        iseg = att_table.loc[streem_info_loc]['ISEG']
        nseg = np.max(iseg)
        stream_up_elv = []
        stream_down_elv = []
        self.nss = nseg  # nu
        for seg in np.arange(1, nseg + 1):
            loc = att_table['ISEG'] == seg
            ireach = att_table.loc[loc]['IREACH']
            strm_top = att_table.loc[loc]['STRM_TOP']
            min_ireach = np.min(ireach)
            max_ireach = np.max(ireach)
            stream_up_elv.append(strm_top[ireach == min_ireach].values[0])
            stream_down_elv.append(strm_top[ireach == max_ireach].values[0])

        self.stream_up_elv = np.array(stream_up_elv)
        self.stream_down_elv = np.array(stream_down_elv)

    def remove_field_num(self, a, i):
        names = list(a.dtype.names)
        new_names = names[:i] + names[i + 1:]
        b = a[new_names]
        return b

    def model(self):
        self.mf = flopy.modflow.Modflow()
        dis = flopy.modflow.ModflowDis(self.mf, nlay=self.nlyars, nrow=self.nrows, ncol=self.ncols,
                                       delr=self.cellsize, delc=self.cellsize,
                                       top=self.top, botm=self.botm,
                                       nper=self.nper, perlen=self.perlen, nstp=self.nstp)


if __name__ == "__main__":
    entry()
    pass
