from __future__ import print_function
import os
import sys
import platform
import zipfile as zf
import flopy as fp
import numpy as np
import shutil as shu
import pandas as pd
from numpy.lib.recfunctions import stack_arrays
from datetime import datetime

'''
__author__ = "Zak Stanko"
__version__ = "07"

Script to drive the sampling of Santa Rosa Plain (SRP) GSFlow model.
Each sample will seed an additional well pumping at 40,000 cubic ft. / day at a specified location.

ARGUMENTS:
    run_num = run number from a set of model runs specified in well_locations.csv
    
REQUIREMENTS:
    well_locations.csv
        has the following columns: run_id, lay, row, col, tlay, blay, nlay
    stream_budget.dat
    stream_budget2.dat
    SRP_0g.wel
    gsflow.exe
    
OUTPUT:
    SRP_model.wel
    zdb_{run_num}.txt (optional)
    run{run_num}.zip (optional)
    
    
Some functions are very tailored to SRP, some are more general.

'''
OPJ = os.path.join
#
vrsn = '07'  # version suffix for file names
mpref = 'SRP'  # model abbreviation used as a prefix on file names
#
# -----------Booleans to control function of script--------------------
# _____________________________________________________________________
process_mnw = True      # Write a new MNW file
process_input = True    # Write a new well file
runme = True            # Run GSFlow
process_output = True   # process and zip up GSFlow output
local = True            # is the script is in the model directory?
clean = False           # delete all model output files when complete?
zdb = False             # debug info printed to zdb_{run_num}.txt
read4nsp = False        # get the first stress period in the stream_budget2.dat file
# ----------------------------------------------------------------------
#
testit = True
if testit:
    process_mnw = False
    process_input = False
    runme = False
    process_output = True
cwdir = os.getcwd()
root = os.path.sep.join(cwdir.split(os.path.sep)[:-1])
fileList = []
if local:
    model_input = OPJ(cwdir, 'modflow', 'input')
    model_output = OPJ(cwdir, 'modflow', 'output')
    prms_output = OPJ(cwdir, 'PRMS', 'output')
    model_dir = OPJ(cwdir, 'windows')
else:  # if not, specify path of model directory
    # project_dir = os.path.normpath('C:/Users/zstanko/Documents/_projects/CAcoastal/_coastal_metamodeling')
    # sample_dir = OPJ(project_dir, 'work', 'trials', '{}_sample_{}'.format(mpref, vrsn))
    # model_dir = os.path.abspath(OPJ(sample_dir, 'SRP_trimmed1990-2000'))
    model_dir = OPJ(cwdir, 'model')
    model_output = OPJ(model_dir, 'output')

model_name = 'rr_tr'  # this is the prefix for model input files
nam_file = model_name + '.nam'  # MODFLOW name file needed for loading the model
last_year = 2015
# load the file
print('loading modflow...')
base_model = fp.modflow.Modflow.load(nam_file, model_ws=model_dir, version='mfnwt', verbose=False,
                                     load_only=['DIS', 'MNW2', 'WEL'])
print('model loaded.')
# This is the original stream budget file from the SFR package (text, not binary)
str_baseline = 'windows/rr_tr_base.sfr.out'
# this the stream budget file with a new well
str_with_well = OPJ(model_output, 'rr_tr.sfr.out')
# read the unchanged mnw file
if len(sys.argv) == 1:  # this is just for when it's being tested
    run_num = 100
    q_gpm = -100  # mean muni pumping is about -100 gpm, domestic -8
    dep_type = 'mnw'
else:
    run_num = int(sys.argv[1])
    q_gpm = float(sys.argv[2])  # mean rural pumping is about -8 gpm
    dep_type = sys.argv[3]

logfile = open('run_{}_{}.log'.format(run_num, dep_type), 'w')
if read4nsp:     # get the first stress period in the stream budget file
    openstrmdat = open(str_baseline, 'r')
    while True:
        line = openstrmdat.readline()
        if line.startswith(' STREAM LISTING'):
            openstrmdat.close()
            break
    a = line.split()
    nsp = int(a[3])
else:
    # set starting sp
    nsp = 1
print('depletion run starts at stress period {}'.format(nsp))
# radius to define local area
# TODO: define radius as a list for multiple local area output
radius = 40  # number of cells in local area radius
newlin = '\n'
#
logfile.write('########### LOG FILE FOR WELLNUM {} ###########{}'.format(run_num, newlin))
logfile.write('Running the Russian River model using {} gpm for the {} package, run number {}{}'.format(q_gpm, dep_type,
                                                                                                      run_num, newlin))
q_constant = 5.451 * q_gpm  # convert to cu m/d and add to each sp of well to be sampled
if dep_type == 'wel':
    welloc_file = OPJ(model_dir, 'well_locations.csv')  # 0-based
    wel_lrc = pd.read_csv(welloc_file)
    #
    # q_rep = np.genfromtxt(OPJ(model_dir, 'meanQts.csv'))  # representative pumping time series
    #
    lrc = wel_lrc.loc[wel_lrc['run_id'] == run_num].values[0]  # 0-based
    r, c = lrc[5], lrc[6]   # already 0-based
    well_rc = [lrc[2] + 1, r + 1, c + 1]
    print('well: row {}, col {}'.format(r+1, c+1))

#####################################################################################
def main():
    global well_rc
    fileList.append('run_{}_{}.log'.format(run_num, dep_type))
    rm = open('readme_{}.txt'.format(run_num), 'w')
    # get the node data so that the stream segments can be analyzed
    if dep_type == 'mnw':
        mnw = fp.modflow.ModflowMnw2.load(OPJ(model_input, 'rr_tr.mnw2'), base_model)
        nodedata = mnw.node_data
        df_nodes = pd.DataFrame.from_records(nodedata, columns=[
            "i",
            "j",
            "ztop",
            "zbotm",
            "wellid",
            "losstype",
            "pumploc",
            "qlimit",
            "ppflag",
            "pumpcap",
            "rw",
            "rskin",
            "kskin",
            "zpump",
        ])
        # load the file that has the list of wells and search for the one to be changed
        df_well_list = pd.read_csv('./windows/mnw_well_list.csv', header=0)
        df = df_well_list.iloc[run_num]
        # the wellnum is the index of the well in each stress period. mnw_well_list.csv
        # was made from the MNW file. get the wellid from the mnw_well_list so you can get the row and col from nodes
        # assume all nodes are in the same row and column
        wellid = df[1]
        df_well_nodes = df_nodes.loc[df_nodes['wellid'] == wellid.upper()]
        # get the row and column for the well.
        well_rc = [1, df[2] + 1, df[3] + 1]
        qloc = [1, df[2], df[3]]
        logfile.write('sampling well number {}, wellid {}{}'.format(run_num, wellid, newlin))
        print('sampling well number {}, wellid {}'.format(run_num, wellid))
        if process_mnw:
            adjust_mnw(wellid, mnw)  # the well for this analysis is in MNW2
        rm.write('this is the run for wellid {}{}'.format(wellid, newlin))
    elif dep_type == 'wel':
        if process_input:
            qloc = adjust_well(run_num)
    #
    #
    la = local_area(run_num, radius, qloc)
    #
    rm.close()
    #
    if runme:
        #
        run_model()
        #

    if process_output:
        #
        original_listfile = OPJ(model_output, 'rr_tr.list')
        listfile = OPJ(model_output, 'rr_tr_{}_{}.list'.format(run_num, dep_type))
        if os.path.isfile(original_listfile) and not os.path.isfile(listfile):
            os.rename(original_listfile, listfile)
        fileList.append(listfile)
        #
        original_gsflow = OPJ(prms_output, 'gsflow.csv')
        gsflowbudget = OPJ(prms_output, 'gsflow_{}_{}.csv'.format(run_num, dep_type))
        if os.path.isfile(original_gsflow) and not os.path.isfile(gsflowbudget):
            os.rename(original_gsflow, gsflowbudget)
        fileList.append(gsflowbudget)
        #
        original_reduction = OPJ(model_output, 'pumping_reduction.out')
        wel_reduction = OPJ(model_output, 'pumping_reduction_{}_{}.out'.format(run_num, dep_type))
        if os.path.isfile(original_reduction) and not os.path.isfile(wel_reduction):
            os.rename(original_reduction, wel_reduction)
        fileList.append(wel_reduction)
        #process_zone(run_num, la, radius)
        #
        process_bhd(run_num, la, radius)
        #
        process_cbc(run_num, la, radius)
        #
        process_list(run_num, la, radius, listfile)
        #
        #gisl(str_baseline, str_with_well, well_rc, radius, run_num)
        #
        process_sfr(run_num, la, radius, str_with_well)
        #
        # copyme(run_num)
        #
        # process a few different local area radii
        #
        # Derek adjust this array to only those you need for your map
        rads = [20] + [radius]
        lal = []
        for rad in rads:
            la = local_area(run_num, rad, qloc)
            process_bhd(run_num, la, rad)
            # process_zone(run_num, la, rad)
            # process_list(run_num, la, rad)
            gisl(str_baseline, str_with_well, well_rc, rad, run_num)
            #
        #
        #rads = [radius] + rads
    zip_up(run_num, rads, qloc)
    #
    if clean:
        clean_up(run_num)


def adjust_mnw(wellid, mnw):
    '''
    Modifies an existing mnw file by adding specified pumping to specified wellnum

    ARGS:
        rn          = unique run number

    REQUIRES THE FOLLOWING GLOBAL VARIABLES:
        model_dir   = directory of model files
        base_model  = flopy modflow instance of baseline model
        q_constant  = constant pumping rate that should be applied

    '''
    #
    mnwin = open('./modflow/input/rr_tr.mnw2', 'r')
    mnwout = open('./modflow/input/rr_tr_new.mnw2', 'w')
    line = mnwin.readline()
    while line.find('Stress')==-1:
        line = mnwin.readline()
        mnwout.write(line)
    while len(line) > 5:
        line = mnwin.readline()
        if line.startswith(wellid.upper()):
            a = line.split()
            pump_rate = float(a[1])
            pump_rate += q_constant
            line = '{:<13}{:.7E}{}'.format(a[0], pump_rate, newlin)

        mnwout.write(line)
    mnwin.close()
    mnwout.close()
    tryflopy = False
    if tryflopy:
        spdata = mnw.stress_period_data
        for sp in range(nsp, base_model.nper+1):
            this_sp = spdata[sp]
            i = 0
            for mnwell in this_sp:
                if mnwell[3] == wellid:
                    pump_rate = float(mnwell[4])
                    # increase pumping
                    pump_rate += q_constant
                    print('well {}; pump {}'.format(spdata[sp][i][3], spdata[sp][i][4]))
                    spdata[sp][i][4] = pump_rate
                    print('well {}; new pump {}'.format(spdata[sp][i][3], spdata[sp][i][4]))
                i += 1
        mnw.stress_period_data = spdata
        # write the new MNW file
        mnw.write_file('../modflow/input/rr_tr_new.mnw2')
    logfile.write('MNW2 pumping increased by {} gpm ({} CMD) for well {}{}'.format(q_gpm, q_constant, wellid, newlin))


def adjust_well(rn):
    '''
    Modifies an existing well file by adding specified pumping to specified (row,col) location
    
    ARGS:
        rn          = unique run number
    
    REQUIRES THE FOLLOWING GLOBAL VARIABLES:
        model_dir   = directory of model files
        base_model  = flopy modflow instance of baseline model
        q_constant  = constant pumping rate that should be applied
        
    '''
    #
    tlay, blay, nlay = lrc[2], lrc[3], lrc[4]
    #rm.write('the well is in row {}, col {}{}'.format(lrc[2], lrc[3], newlin))
    #
    #opt_line = 'specify 0.1 1021'
    #options = fp.utils.OptionBlock(opt_line, fp.modflow.ModflowWel, block=True)
    wel = fp.modflow.ModflowWel.load(OPJ(model_input, 'rural_pumping_base.wel'), base_model)
    # need to change SP range for restart simulation, which starts at SP 184 (183, 0-based)

    for sp in range(nsp-1, base_model.nper):
        spq = wel.stress_period_data[sp]
        mask = (spq['i'] == r) & (spq['j'] == c)
        mwl = spq[mask]
        wi = np.where(mask)[0]  # well indices in SP data for current well
        #
        q_sum = mwl['flux'].sum()
        # q_new = q_constant/np.float32(len(wi))
        # if well is in a new location (i.e., not in existing well file), need to add to SP data
        if len(mwl) == 0:
            q_new = q_constant/nlay
            # following chunk is modified from streamcapture.py (gw1774 training)
            welbase = np.recarray.copy(wel.stress_period_data[sp])
            newwells = np.recarray.copy(wel.stress_period_data[sp])
            for nl in range(nlay):
                scwell = np.recarray(1, welbase.dtype)
                scwell['k'], scwell['i'], scwell['j'] = tlay + nl, r, c
                scwell['flux'] = q_new
                newwells = stack_arrays((newwells, scwell), asrecarray=True, usemask=False)
            wel.stress_period_data[sp] = newwells
        else:
            q_new = q_constant
            for i, w in enumerate(mwl):
                q_rate = w['flux']
                if q_sum == 0.0:
                    q_frac = 1.0
                    # q_adjust = q_new/np.float32(nlay)
                    q_adjust = q_new/np.float32(len(wi))
                else:
                    q_frac = q_rate/q_sum
                    q_adjust = q_rate + q_new * q_frac
                wel.stress_period_data[sp][wi[i]]['flux'] = q_adjust
                if zdb:
                    str1 = 'sp {}, well flux in lay {}, row {}, col {}, '.format(sp + 1, w[0] + 1, r + 1, c + 1)
                    str2 = 'changed from {} to {} \n'.format(q_rate, q_adjust)
        #
    #
    wel.fn_path = OPJ(model_input, 'rural_pumping.wel')
    wel.write_file()
    # the written well file doesn't have the options block b/c flopy doesn't support it, so ..
    #DEREK - you may not need to do any of this.
    #shu.move(OPJ(model_dir, 'SRP_model.wel'), OPJ(model_dir, 'SRP_model_old.wel'))
    #oldwellfile = OPJ(model_dir, 'SRP_model_old.wel')
    #newwellfile = OPJ(model_dir, 'SRP_model.wel')
    #fold = open(oldwellfile)
    #line = fold.readline()  # read to junk
    #fnew = open(newwellfile, 'w')

    #fnew.write('# Well file modified to include OPTIONS block \n')
    #fnew.write('OPTIONS\n')
    #fnew.write('SPECIFY        0.02         50\n')
    #fnew.write('END\n')
    #shu.copyfileobj(fold, fnew)
    logfile.write('WEL pumping increased by {} gpm ({} CMD){}'.format(q_gpm, q_constant, newlin))
    #
    wellout = open(OPJ(model_input, 'rural_pumping_new.wel'), 'w')
    for line in open(OPJ(model_input, 'rural_pumping.wel'), 'r'):
        if line.startswith('#'):
            wellout.write(line)
            line = 'OPTIONS{0:}SPECIFY 0.1 1021{0:}END{0:}'.format(newlin)
        wellout.write(line)
    wellout.close()
    shu.copyfile(OPJ(model_input, 'rural_pumping_new.wel'), OPJ(model_input, 'rural_pumping.wel'))
    return [0, r, c]


def run_model():

    if 'window' in platform.platform().lower():
        pref = ''
    else:
        pref = './'
    logfile.write('gsflow started at {}{}'.format(datetime.today(), newlin))
    # os.system("{0}gsflow.exe prms_v3_cont.control".format(pref))

    #gsf = OPJ(pref, model_dir, 'gsflow_ag.exe')
    gsf = OPJ(pref, 'gsflow.exe')
    # control file name updated
    os.chdir(model_dir)
    control_file = OPJ(model_dir, 'gsflow_rr.control -set end_time {},12,31,0,0,0'.format(last_year))
    #os.system('))
    os.system('{} {}'.format(gsf, control_file))
    logfile.write('gsflow finished at {}{}'.format(datetime.today(), newlin))
    os.chdir(cwdir)
    return


def local_area(rn, en, qloc):
    '''
    creates a circular local zone around a point of interest
    
    INPUT:
        rn      = unique model run number 
        en      = number of model cells that define the radius of the local zone
        qloc    = location of the center of the zone in the form: (rn, lay, row, col) 
        
    OUTPUT:
        ladf    = dataframe of row, col for all cells in the local area 
        local_area_{rn}_{en}.csv and local_area_{rn}_{en}.txt are written to CWD
        
    '''
    print('running local area...')
    r, c = qloc[1], qloc[2]
    #  define cells within local area
    rl, ru = r - en, r + en + 1
    cl, cu = c - en, c + en + 1
    if ru > base_model.nrow:
        ru = base_model.nrow - 1
    elif rl < 0:
        rl = 0
    if cu > base_model.ncol:
        cu = base_model.ncol - 1
    elif cl < 0:
        cl = 0
    larc = []
    for ri in range(rl, ru):
        for ci in range(cl, cu):
            dist = ((r - ri) ** 2.0 + (c - ci) ** 2.0) ** 0.5
            if dist < en:
                larc.append((ri, ci, dist))
    ladf = pd.DataFrame(larc)
    ladf.columns = ['row', 'col', 'distance']
    la_file = OPJ(cwdir, 'local_area_{}_r{}_{}.csv'.format(rn, en, dep_type))
    fileList.append(la_file)
    with open(la_file, 'w') as la:
        str1 = 'local area \n'
        str2 = 'row top, {}, row bottom, {} \n'.format(rl, ru)
        str3 = 'col left, {}, col right, {} \n'.format(cl, cu)
        la.write(str1+str2+str3)
    ladf.to_csv(OPJ(cwdir, 'local_area_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    print('made {}'.format(OPJ(cwdir, 'local_area_{}_r{}_{}.csv'.format(rn, en, dep_type))))
    fileList.append(OPJ(cwdir, 'local_area_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    #
    return ladf


def process_bhd(rn, ladf, en):
    '''
    processes binary head (BHD) output
    
    INPUT:
        rn      = unique model run number 
        en      = number of model cells that define the radius of the local zone
        ladf    = local area dataframe from local_area()
        
    OUTPUT:
        local_heads_{rn}_r{en}.csv
        final_heads_{rn}_r{en}.npy
        local_heads_{rn}_r{en}.npy
        
    '''
    print('processing binary heads...')
    bhd = fp.utils.HeadFile(OPJ(model_output, '{}.hds'.format(model_name)))
    # times = bhd.get_times()
    kskp = bhd.get_kstpkper()
    rows = ladf.row.values
    cols = ladf.col.values
    hd_lrc = []  # make l,r,c header for saving output
    for l in range(base_model.nlay):
        for it in ladf.itertuples():
            hd_lrc.append('l{}r{}c{}'.format(l, it[1], it[2]))
    #
    hds = []
    for i, kk in enumerate(kskp):
        hd = bhd.get_data(kstpkper=kk)
        head_en = hd[:, rows, cols]
        hds.append(head_en.ravel())
    # colnam = 'SP{}'.format(kk[1])
    localhds = pd.DataFrame(hds)
    localhds.to_csv(OPJ(cwdir, 'local_heads_{}_r{}_{}.csv'.format(rn, en, dep_type)), header=hd_lrc)
    fileList.append(OPJ(cwdir, 'local_heads_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    # save final head
    finalhead = bhd.get_data(kstpkper=kskp[-1])
    finalhead = np.array(finalhead[0], dtype=float)
    fname = OPJ(cwdir, 'final_heads_{}_r{}_{}.csv'.format(rn, en, dep_type))
    np.save(fname, finalhead)
    fileList.append(fname)
    print('saved {}'.format(fname))
    logfile.write('saved {}'.format(fname))
    #np.save(OPJ('local_heads_{}_r{}'.format(rn, en)), localhds)
    return


def process_cbc(rn, ladf, en):
    '''
    processes cell-by-cell (CBC) budget output
    
    INPUT:
        rn      = unique model run number 
        en      = number of model cells that define the radius of the local zone
        ladf    = local area dataframe from local_area()
        
    OUTPUT:
        local_storage_{rn}_r{en}.csv
        local_leakage_{rn}_r{en}.csv
        
    '''
    cbc = fp.utils.CellBudgetFile(OPJ(model_output, '{}.cbc'.format(model_name)))
    kskp = cbc.get_kstpkper()
    rows = ladf.row.values
    cols = ladf.col.values
    hd_lrc = []  # make l,r,c header for saving output
    for l in range(base_model.nlay):
        for it in ladf.itertuples():
            hd_lrc.append('l{}r{}c{}'.format(l, it[1], it[2]))
    #
    stor = []
    for i, kk in enumerate(kskp):
        st = cbc.get_data(kstpkper=kk, text='STORAGE', full3D=True)[0]
        stor_en = st[:, rows, cols]
        stor.append(stor_en.ravel())
    localstor = pd.DataFrame(stor)
    localstor.to_csv(OPJ(cwdir, 'local_storage_{}_r{}_{}.csv'.format(rn, en, dep_type)), header=hd_lrc)
    fileList.append(OPJ(cwdir, 'local_storage_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    #
    # following chunk was used to verify values in CBC file are equal to those in stream_budget.dat
    leak = []
    for i, kk in enumerate(kskp):
        sl = cbc.get_data(kstpkper=kk, text='STREAM LEAKAGE', full3D=True)[0]
        leak_en = sl[:, rows, cols]
        leak.append(leak_en.ravel())
    localleak = pd.DataFrame(leak)
    localleak.to_csv(OPJ(cwdir, 'local_leakage_{}_r{}_{}.csv'.format(rn, en, dep_type)), header=hd_lrc)
    fileList.append(OPJ(cwdir, 'local_leakage_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    #
    # finalbud = cbc.get_data(kstpkper=kskp[-1], text='STORAGE', full3D=True)
    # np.save(OPJ('final_storage_{}'.format(rn)), finalbud)
    # finalleak = cbc.get_data(kstpkper=kskp[-1], text='STREAM LEAKAGE', full3D=True)
    # np.save(OPJ('final_leakage_{}'.format(rn)), finalleak)
    return


def process_zone(rn, ladf, en):
    '''
    processes cell-by-cell (.cbc) and UZF (.uzfb0) budget output with flopy ZoneBudget class
    
    INPUT:
        rn      = unique model run number 
        en      = number of model cells that define the radius of the local zone
        ladf    = local area dataframe from local_area()
        
    OUTPUT:
        zone_cbc_netflux_{rn}_r{en}.csv
        zone_uzf_netflux_{rn}_r{en}.csv
        
    '''
    rows = ladf.row.values
    cols = ladf.col.values
    zon = np.zeros([base_model.nlay, base_model.nrow, base_model.ncol], dtype=int)
    zon[:, rows, cols] = 1
    run_cbf = OPJ(model_output, '{}.cbc'.format(model_name))
    print(run_cbf)
    run_uzf = OPJ(model_output, '{}.uzfb0'.format(model_name))
    run_zb = fp.utils.ZoneBudget(run_cbf, zon)
    run_uz = fp.utils.ZoneBudget(run_uzf, zon)
    zb_names = run_zb.get_record_names()
    # print(zb_names)
    uz_names = run_uz.get_record_names()
    # print(uz_names)
    # uz_names = uz_names[:14]
    # get dataframes of each net budget component
    # run_df_netzb = run_zb.get_dataframes(names=zb_names, start_datetime='01-01-1990', net=True)
    run_df_zb = run_zb.get_dataframes(names=zb_names, start_datetime='01-01-1974')
    # run_df_netuz = run_uz.get_dataframes(names=uz_names, start_datetime='01-01-1990', net=True)
    run_df_uz = run_uz.get_dataframes(names=uz_names, start_datetime='01-01-1974')
    # create single index dataframe
    idx = run_df_zb.index.levels
    nc = len(idx[1])
    rdf_zb = pd.DataFrame(run_df_zb.values.reshape(-1, nc), index=idx[0].values, columns=idx[1].values)
    idx = run_df_uz.index.levels
    nc = len(idx[1])
    rdf_uz = pd.DataFrame(run_df_uz.values.reshape(-1, nc), index=idx[0].values, columns=idx[1].values)
    # define column names to use in merged dataset
    # zbn = ['STORAGE', 'WELLS', 'STREAM_LEAKAGE', 'ZONE_0', 'HEAD_DEP_BOUNDS']
    # uzn = ['GW_ET', 'SURFACE_LEAKAGE', 'UZF_RECHARGE']
    # rdf = pd.concat([rdf_netzb, rdf_netuz], axis=1)
    # rdf['sum'] = rdf[zbn + uzn].sum(axis=1)
    rdf_zb.to_csv(OPJ(cwdir, 'zone_uzf_all_{}_r{}_{}.csv'.format(rn, en, dep_type)))  # columns may be out of order
    rdf_uz.to_csv(OPJ(cwdir, 'zone_uzf_all_{}_r{}_{}.csv'.format(rn, en, dep_type)))  # columns may be out of order
    return
    
    
def process_list(rn, ladf, en, listfile):
    '''
    processes main listing (.list) output.
    Assumes that reduced pumping was written to a separate file called reduced_wells.txt
    
    INPUT:
        rn      = unique model run number 
        en      = number of model cells that define the radius of the local zone
        ladf    = local area dataframe from local_area()
        
    OUTPUT:
        reduced_wells_{rn}_r{en}.csv
        flux_budget_{rn}.csv
        vol_budget_{rn}.csv
        
    '''
    mfl = fp.utils.MfListBudget(listfile)
    df_flux, df_vol = mfl.get_dataframes(start_datetime='01-01-1990')
    fname = OPJ(cwdir, 'flux_budget_{}_{}.csv'.format(rn, dep_type))
    df_flux.to_csv(fname, index_label='date')
    fileList.append(fname)
    logfile.write('flux budget extracted from list file, saved as {}{}'.format(fname, newlin))
    fname = OPJ(cwdir, 'vol_budget_{}_{}.csv'.format(rn, dep_type))
    df_vol.to_csv(fname, index_label='date')
    fileList.append(fname)
    logfile.write('volumetric budget extracted from list file, saved as {}{}'.format(fname, newlin))
    return


def get_stream_loss(infile, well_location, rad):
    '''
    Searches the stream budget output for stream flux within a local area around a point of interest.
    
    INPUT:
        infile          = stream budget file written by SFR package
        well_location   = row, col location for the point of interest. 1-based
        rad             = radius around which the search will save stream flux 
        
    OUTPUT:
        str_aqu_flow            = total stream flux within local area for each stress period
        stress_period_number    = stress period where total stream flux is saved
        
    '''
    stress_period_number = []
    str_aqu_flow = []
    is_1st_stress = True
    cumulative_loss = 0
    for line in infile:
        #
        if line[0:7] == " STREAM":
            line = line.split()
            if float(line[5]) < 20:
                curr_time = float(line[3]) - 0.5
            else:
                curr_time = float(line[3])
            if not is_1st_stress:
                stress_period_number.append(curr_time)
                str_aqu_flow.append(cumulative_loss)
            cumulative_loss = 0
            is_1st_stress = False
        #
        elif line[0:6] == " LAYER":
            z = 1
        elif line == "\n" or line[0:16] == "                ":
            pass
        else:
            line = line.split()
            line = [float(rec) for rec in line]
            dist = ((well_location[1] - line[1])**2.0 + (well_location[2] - line[2])**2.0)**0.5
            if dist <= rad:
                # get stream loss
                cumulative_loss += float(line[6])
        #
    return str_aqu_flow, stress_period_number


def gisl(str_base, str_2, well_location, rad, rn):
    '''
    calculates the difference between two calls to get_stream_loss()
    one for baseline model and one for a seeded well run.
    
    INPUT:
        str_base        = baseline stream budget output
        str_2           = stream budget output for perturbed run
        well_location   = row, col location for the point of interest. 1-based
        rad             = radius around which the search will save stream flux 
        rn              = unique model run number
        
    OUTPUT:
        stream_depletion_{rn}_r{rad}.txt
        
    '''
    print('calculating stream loss (gisl), rad={}'.format(rad))
    logfile.write('processing SFR budget for stream depletion...{}'.format(newlin))
    with open(str_base) as infile1, open(str_2) as infile2:
        baseline_streamloss, timeseries = get_stream_loss(infile1, well_location, rad)
        np.savetxt('streamloss_{}_r{}_base.txt'.format(rn, rad), baseline_streamloss)
        fileList.append('streamloss_{}_r{}_base.txt'.format(rn, rad))
        logfile.write('{} saved.{}'.format('streamloss_{}_r{}_base.txt'.format(rn, rad), newlin))
        # np.savetxt('timeseries_base.csv', timeseries, delimiter=',')
        streamloss, timeseries2 = get_stream_loss(infile2, well_location, rad)
        np.savetxt('streamloss_{}_r{}_{}.txt'.format(rn, rad, dep_type), streamloss)
        fileList.append('streamloss_{}_r{}_{}.txt'.format(rn, rad, dep_type))
        logfile.write('saved streamloss_{}_r{}_{}.txt{}'.format(rn, rad, dep_type, newlin))
        np.savetxt('timeseries_{}_{}.csv'.format(rn, dep_type), timeseries2, delimiter=',')
        fileList.append('timeseries_{}_{}.csv'.format(rn, dep_type))
        logfile.write(('saved timeseries_{}_{}.csv{}'.format(rn, dep_type, newlin)))
        # if the two files have different number of stress periods, make them the same size
    # other code should prevent this, but just in case
    new_strm_loss = np.array(streamloss)
    baseline_loss = np.array(baseline_streamloss)
    if len(new_strm_loss) < len(baseline_loss):
        baseline_loss = baseline_loss[:len(new_strm_loss)]
    if len(baseline_loss) < len(new_strm_loss):
        new_strm_loss = new_strm_loss[:len(baseline_loss)]
    stream_depletion = new_strm_loss - baseline_loss
    np.savetxt(OPJ(cwdir, 'stream_depletion_{}_r{}_{}.txt'.format(rn, rad, dep_type)), stream_depletion, delimiter=',')
    fileList.append(OPJ(cwdir, 'stream_depletion_{}_r{}_{}.txt'.format(rn, rad, dep_type)))
    return


def process_sfr(rn, ladf, en, sfr_file):
    """
    :param rn:
    :param ladf:
    :param en:
    :param sfr_file:
    :return:
    """
    sfrout = fp.utils.SfrFile(sfr_file)
    sfrdf = sfrout.get_dataframe()
    # index sfr output for reaches within local area
    ladf['rowcol'] = list(zip(ladf.row, ladf.col))
    sfrdf['rowcol'] = list(zip(sfrdf.row, sfrdf.column))
    select = sfrdf['rowcol'].isin(ladf['rowcol'])
    sfrdf = sfrdf.loc[select, :]
    fname = OPJ(cwdir, 'sfr_df_{}_r{}_{}.csv'.format(rn, en, dep_type))
    sfrdf.to_csv(fname, index_label='index')
    fileList.append(fname)
    logfile.write('extracting sfr budget to {}{}'.format(fname, newlin))
    #


def copyme(rn):
    f1 = OPJ(model_dir, 'OUTPUT_SRP_gsflow.csv')
    shu.copy(f1, cwdir)
    f1 = OPJ(model_dir, 'OUTPUT_SRP_gsflow.out')
    shu.copy(f1, cwdir)
    return


def zip_up(rn, ens, qloc):
    # All files that are made are added to fileList
    zipfilename = OPJ(cwdir, 'run{}_{}.zip'.format(rn, dep_type))
    print('zipping up run {} as {}'.format(rn, zipfilename))
    logfile.write('zipping up run {} as {}{}'.format(rn, zipfilename, newlin))
    #print('run number {} adjusts wells in row {} and col {}'.format(qloc[1] + 1, qloc[2] + 1))

    files = np.unique(fileList)
    with zf.ZipFile(zipfilename, 'w', zf.ZIP_DEFLATED) as zp:
        for f in files:
            if f.endswith('.log'):
                logfile.close()
            addfile2zip(zp, f)
    zipsize = os.path.getsize(zipfilename)
    print('results saved in {} ({} MB)'.format(zipfilename, zipsize))
    #logfile.write('results saved in {} ({} MB){}'.format(zipfilename, zipsize, newlin))
    return


def addfile2zip(zp, filename):
    if os.path.isfile(filename):
        #print('found {} and zipping it...'.format(filename))
        #logfile.write('found {} and zipping it...{}'.format(filename, newlin))
        zp.write(filename, os.path.basename(filename))
        os.remove(filename)
    else:
        print('{} was not found.'.format(filename))
        #logfile.write('{} was not found.{}'.format(filename, newlin))
    return zp


def clean_up(rn):
    for f in fileList:
        os.remove(f)
    return


if __name__ == '__main__':
    main()

