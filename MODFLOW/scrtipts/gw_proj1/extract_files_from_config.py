import os, sys
import configparser
import shutil

config_file = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\gw_proj\rr_ss_config.ini"
config = configparser.ConfigParser()
config.read(config_file)

dst_folder = r"D:\trash\init_files"
init_base = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\gw_proj"

init_items = list(config.items())
for item in init_items:
    section_items = list(item[1].items())
    for sitem in section_items:
        if os.path.isfile(sitem[1]):
            fn = sitem[1]
            folder = os.path.dirname(fn)
            if folder == '':
                folder = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\gw_proj"
            basename = os.path.splitext(os.path.basename(fn))[0]
            file_list = os.listdir(folder)
            for f in file_list:
                if basename in f:
                    print("copying {}".format(f))
                    src = os.path.join(folder, f)
                    dst = os.path.join(dst_folder, f)
                    shutil.copy(src, dst)


