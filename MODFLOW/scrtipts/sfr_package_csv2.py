"""
Disclaimer: This information is preliminary and is subject to revision. It is being provided to meet the need for
timely best science. The information is provided on the condition that neither the U.S. Geological Survey nor the U.S.
Government shall be held liable for any damages resulting from the authorized or unauthorized use of the information.
"""

import sys, os
import flopy
import numpy as np
import pandas as pd

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
    main()
    pass
