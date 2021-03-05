import os, sys
class Include(object):
    def __init__(self):
        print ("Read File names to be used in generating the model files ....")
        self.get_file_names()
        print ("Done .....")

        #-------------------------------------------------------------
        ## ---------- Global Variables-------------------------------
        #------------------------------------------------------------
        # general grid infor
        self.origin_m = [465900.0, 4361700.0]
        self.origin_ft = [465900.0 * 3.28084, 4361700.0 * 3.28084]
        self.cellsize = 300.0

        # Fields for the geological framework
        self.geo_info['Fields_name'] = {'top1':'YF_tp', 'top2':'OF_tp', 'top3':'Fbrk_tp', 'bot': 'Bmt_nf'}




    def get_file_names (self):
        """
        This function populates a dictionary with all files name that are needed to generate input files
        :return:
        return a dictionary with file names
        """
        files_dict = dict()

        ## --- Shape Files
        # Hru_param file
        read_binary = True
        save_binary = True
        self.hru_parm_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_param_tzones_subbasin_pzones.shp"
        self.binary_hru_file = r"D:\Workspace\projects\RussianRiver\modflow\other_files\hru_param.dat "
        self.hru_info = {'read_binary':read_binary, 'save_binary':save_binary, 'shp_file': self.hru_parm_file,
                         'binary_file': self.binary_hru_file}

        # geology
        read_binary = True
        save_binary = True
        self.geology_file = r"D:\Workspace\projects\RussianRiver\Data\geology\RR_gfm_grid_1.8_gsflow.shp"
        self.binary_geo_file = r"D:\Workspace\projects\RussianRiver\modflow\other_files\geo_hru_param.dat"
        self.geo_info = {'read_binary': read_binary, 'save_binary': save_binary, 'shp_file': self.geology_file,
                         'binary_file': self.binary_geo_file}
        self.grid_file_m = r"D:\Workspace\projects\RussianRiver\modflow\other_files\grid\rr_grid_0.npy"

        # executable
        self.mdfexe = r"D:\Workspace\bin\MODFLOW-NWT_1.1.3\bin\MODFLOW-NWT"

        # budget file
        self.budget = r"D:\Workspace\projects\RussianRiver\modflow\other_files\budget.xlsx"


    def read_file_names_from_file(self, name):
        pass
