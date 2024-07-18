# import python packages
import os
import glob
import re
import shutil
import gsflow


def main(script_ws, climate_change_scenario):

    # define constants
    newlin = '\n'

    # define replacenth function
    def replacenth(string, sub, wanted, n):
        where = [m.start() for m in re.finditer(sub, string)][n - 1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, wanted, 1)
        newString = before + after
        return newString

    # set all inputs folder
    all_inputs_folder = os.path.join(script_ws, "..", "all_inputs")

    # generate new model folder structure
    gsflow_model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")
    windows_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "windows")
    modflow_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "modflow")
    modflow_input_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "modflow", "input")
    modflow_output_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "modflow", "output")
    prms_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "PRMS")
    prms_input_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "PRMS", "input")
    prms_output_ws = os.path.join(script_ws, "..", "gsflow_model_updated", "PRMS", "output")
    os.mkdir(gsflow_model_ws)
    os.mkdir(windows_ws)
    os.mkdir(modflow_ws)
    os.mkdir(modflow_input_ws)
    os.mkdir(prms_ws)
    os.mkdir(prms_input_ws)

    # move modflow output files
    modflow_output_old_ws = os.path.join(script_ws, "..", "modout")
    os.rename(modflow_output_old_ws, modflow_output_ws)

    # move prms output files
    prms_output_old_ws = os.path.join(script_ws, "..", "prmsout")
    os.rename(prms_output_old_ws, prms_output_ws)

    # move windows files
    shutil.move(os.path.join(all_inputs_folder, 'bin'), os.path.join(windows_ws))
    extensions = ['.exe', '.control', '.py', '.nam', '.sqlite', '.bat', '.zon', '.txt', '.waprj', '.xy']
    for ext in extensions:
        this_ext = '*' + ext
        ext_file_path = os.path.join(all_inputs_folder, this_ext)
        files_with_ext = glob.glob(ext_file_path)
        for file in files_with_ext:
            shutil.move(file, windows_ws)

    # move modflow input files
    shutil.move(os.path.join(all_inputs_folder, 'ag_diversions'), os.path.join(modflow_input_ws))
    extensions = ['.ag', '.bas', '.dat', '.dis', '.gage', '.ghb', '.hfb', 'hob', '.lak', '.mnw2', '.mnwi', '.nwt', '.oc', '.sfr', '.upw', '.uzf', '.wel']
    for ext in extensions:
        this_ext = '*' + ext
        ext_file_path = os.path.join(all_inputs_folder, this_ext)
        files_with_ext = glob.glob(ext_file_path)
        for file in files_with_ext:
            shutil.move(file, modflow_input_ws)

    # move prms input files
    extensions = ['.data', '.param']
    for ext in extensions:
        this_ext = '*' + ext
        ext_file_path = os.path.join(all_inputs_folder, this_ext)
        files_with_ext = glob.glob(ext_file_path)
        for file in files_with_ext:
            shutil.move(file, prms_input_ws)


    # update file names in modflow/inputs
    mark_west_old = os.path.join(modflow_input_ws, "Mark_West_inflow_" + climate_change_scenario + ".dat")
    mark_west_new = os.path.join(modflow_input_ws, "Mark_West_inflow.dat")
    os.rename(mark_west_old, mark_west_new)

    rr_climate_files = glob.glob(os.path.join(modflow_input_ws, "rr_climate.*")) # do non-heavy files
    for rr_climate_file in rr_climate_files:
        rr_climate_file_old = rr_climate_file
        rr_climate_file_new = rr_climate_file.replace('rr_climate', 'rr_tr')
        os.rename(rr_climate_file_old, rr_climate_file_new)

    rr_climate_files = glob.glob(os.path.join(modflow_input_ws, "rr_climate_heavy.*"))  # do heavy files
    for rr_climate_file in rr_climate_files:
        rr_climate_file_old = rr_climate_file
        rr_climate_file_new = rr_climate_file.replace('rr_climate', 'rr_tr')
        os.rename(rr_climate_file_old, rr_climate_file_new)

    # update file names in prms/inputs
    prms_data_old = os.path.join(prms_input_ws, climate_change_scenario + "_rr_corrected_future.data")
    prms_data_new = os.path.join(prms_input_ws, "prms_rr.data")
    os.rename(prms_data_old, prms_data_new)

    # change file paths in name files
    name_file_path_in = os.path.join(windows_ws, 'rr_' + climate_change_scenario + '_heavy.nam')
    name_file_path_out = os.path.join(windows_ws, 'rr_tr_heavy.nam')
    name_file_out = open(name_file_path_out, 'w')
    for line in open(name_file_path_in, 'r'):
        if '.list' in line:
            line = line.replace('rr_climate' + climate_change_scenario + '.list', 'rr_tr.list')
        if 'rr_climate' in line:
            line = line.replace('rr_climate', 'rr_tr')
        if '\\modout' in line:
            line = line.replace('\\modout', '.\\modflow\\output')
        else:
            if '\t' in line:
                line = replacenth(line, '\t', '\t..\\modflow\\input\\', 2)

        name_file_out.write(line)
    name_file_out.close()

    # update file paths in control files for heavy modsim-gsflow file
    control_file_path_in = os.path.join(windows_ws, 'gsflow_rr_' + climate_change_scenario + '_heavy_modsim_orig.control')
    control_file_path_out = os.path.join(windows_ws, 'gsflow_rr_' + climate_change_scenario + '_heavy_modsim.control')
    shutil.copy2(control_file_path_out, control_file_path_in)
    os.remove(control_file_path_out)
    control_file_out = open(control_file_path_out, 'w')
    for line in open(control_file_path_in, 'r'):
        if 'rr_' + climate_change_scenario + '_heavy.nam' in line:
            line = line.replace('rr_' + climate_change_scenario + '_heavy.nam', 'rr_tr_heavy.nam')
        if  climate_change_scenario + '_rr_corrected_future.data' in line:
            line = line.replace('.\\prmsout\\' + climate_change_scenario + '_rr_corrected_future.data', '..\\PRMS\\input\\prms_rr.dat')
        if 'prms_rr.param' in line:
            line = line.replace('prms_rr.param', '..\\PRMS\\input\\prms_rr.param')
        if 'ag_pond_HRUs.param' in line:
            line = line.replace('ag_pond_HRUs.param', '..\\PRMS\\input\\ag_pond_HRUs.param')
        if '.\\prmsout\\RR_gsflow.out' in line:
            line = line.replace('.\\prmsout\\RR_gsflow.out', '..\\PRMS\\output\\RR_gsflow.out')
        if '.\\prmsout\\gsflow_' + climate_change_scenario + '.csv' in line:
            line = line.replace('.\\prmsout\\gsflow_' + climate_change_scenario + '.csv', '..\\PRMS\\output\\gsflow.csv')
        if 'prms_ic.in' in line:
            line = line.replace('prms_ic.in', '..\\PRMS\\input\\prms_ic.in')
        if 'prms_ic_prms.out' in line:
            line = line.replace('.\\prmsout\\prms_ic_prms.out', '..\\PRMS\\output\\prms_ic_prms.out')
        if '.\\prmsout\\nsub_' in line:
            line = line.replace('.\\prmsout\\nsub_', '..\\PRMS\\output\\nsub_')
        if '.\\prmsout\\nhru_' in line:
            line = line.replace('.\\prmsout\\nhru_', '..\\PRMS\\output\\nhru_')
        if '.\\prmsout\\statvar_prms.dat' in line:
            line = line.replace('.\\prmsout\\statvar_prms.dat', '..\\PRMS\\output\\statvar_prms.dat')

        control_file_out.write(line)
    control_file_out.close()
    os.remove(control_file_path_in)


    # update file paths in control files for heavy gsflow file
    control_file_path_in = os.path.join(windows_ws, 'gsflow_rr_' + climate_change_scenario + '_heavy_orig.control')
    control_file_path_out = os.path.join(windows_ws, 'gsflow_rr_' + climate_change_scenario + '_heavy.control')
    shutil.copy2(control_file_path_out, control_file_path_in)
    os.remove(control_file_path_out)
    control_file_out = open(control_file_path_out, 'w')
    for line in open(control_file_path_in, 'r'):
        if 'rr_' + climate_change_scenario + '_rcp45_heavy.nam' in line:
            line = line.replace('rr_' + climate_change_scenario + '_heavy.nam', 'rr_tr_heavy.nam')
        if climate_change_scenario + '_rr_corrected_future.data' in line:
            line = line.replace('.\\prmsout\\'  + climate_change_scenario + '_rr_corrected_future.data', '..\\PRMS\\input\\prms_rr.dat')
        if 'prms_rr.param' in line:
            line = line.replace('prms_rr.param', '..\\PRMS\\input\\prms_rr.param')
        if 'ag_pond_HRUs.param' in line:
            line = line.replace('ag_pond_HRUs.param', '..\\PRMS\\input\\ag_pond_HRUs.param')
        if '.\\prmsout\\RR_gsflow.out' in line:
            line = line.replace('.\\prmsout\\RR_gsflow.out', '..\\PRMS\\output\\RR_gsflow.out')
        if '.\\prmsout\\gsflow_' + climate_change_scenario + '.csv' in line:
            line = line.replace('.\\prmsout\\gsflow_'  + climate_change_scenario + '.csv', '..\\PRMS\\output\\gsflow.csv')
        if 'prms_ic.in' in line:
            line = line.replace('prms_ic.in', '..\\PRMS\\input\\prms_ic.in')
        if 'prms_ic_prms.out' in line:
            line = line.replace('.\\prmsout\\prms_ic_prms.out', '..\\PRMS\\output\\prms_ic_prms.out')
        if '.\\prmsout\\nsub_' in line:
            line = line.replace('.\\prmsout\\nsub_', '..\\PRMS\\output\\nsub_')
        if '.\\prmsout\\nhru_' in line:
            line = line.replace('.\\prmsout\\nhru_', '..\\PRMS\\output\\nhru_')
        if '.\\prmsout\\statvar_prms.dat' in line:
            line = line.replace('.\\prmsout\\statvar_prms.dat', '..\\PRMS\\output\\statvar_prms.dat')
        control_file_out.write(line)
    control_file_out.close()
    os.remove(control_file_path_in)

    # update file paths in zone budget txt files
    zone_bud_files_in = [os.path.join(windows_ws, 'zb_cmd_gwbasin_orig.txt'),
                         os.path.join(windows_ws, 'zb_cmd_northsouth_orig.txt'),
                         os.path.join(windows_ws, 'zb_cmd_subbasins_orig.txt'),
                         os.path.join(windows_ws, 'zb_cmd_watershed_orig.txt')]
    zone_bud_files_out = [os.path.join(windows_ws, 'zb_cmd_gwbasin.txt'),
                          os.path.join(windows_ws, 'zb_cmd_northsouth.txt'),
                          os.path.join(windows_ws, 'zb_cmd_subbasins.txt'),
                          os.path.join(windows_ws, 'zb_cmd_watershed.txt')]

    for zone_bud_file_in, zone_bud_file_out in zip(zone_bud_files_in, zone_bud_files_out):

        shutil.copy2(zone_bud_file_out, zone_bud_file_in)
        os.remove(zone_bud_file_out)
        zone_bud_out = open(zone_bud_file_out, 'w')

        for line in open(zone_bud_file_in, 'r'):
            if 'modout' in line:
                line = line.replace('modout', '..\\modflow\\output')
            zone_bud_out.write(line)
        zone_bud_out.close()
        os.remove(zone_bud_file_in)





# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, climate_change_scenario)
