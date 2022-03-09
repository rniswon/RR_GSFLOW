
""""
The goal of this class to allow user to add and remove new segments or lakes to/from an existing stream network.
"""
import flopy
# TODO:
# change NSTRM : number of reaches
# change

class SFR_editor(object):
    def __init__(self, mf_nam = None):
        """
        :param flopy_obj: is a flopy object that has at least DIS, BAS6, SFR package (and LAK if needed)
        """
        self.mf = flopy.modflow.Modflow.load(mf_nam, load_only=['DIS', 'BAS6', 'SFR'], forgive=False)
        pass

    def add_segment(self):
        pass

    def remove_segment(self):
        pass




if __name__ == "__main__":
    fm_name = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Steady_state\rr_ss_v0.nam"

    sfr = SFR_editor(mf_nam = fm_name)


