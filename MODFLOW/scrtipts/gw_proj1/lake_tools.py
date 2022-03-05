import os, sys
import flopy
import gsflow
from gw_utils.general_util import get_mf_files


def remove_lakes(mf, lake_ids = []):
    pass


if __name__ == "__main__":
    ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220228_01\windows"
    fname = "rr_tr.nam"
    model_files = get_mf_files(os.path.join(ws, fname))
    mf = flopy.modflow.Modflow.load(fname,model_ws=ws, load_only=['DIS', 'BAS6', 'SFR', 'LAK'] )