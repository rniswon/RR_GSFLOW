import os, sys
import gsflow

folder = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version_ayman\windows"
control_name = r"gsflow_rr.control"


gs = gsflow.GsflowModel.load_from_file(os.path.join(folder, control_name), mf_load_only=['DIS', 'BAS6', 'UPW', 'UZF'])


cc = 1
