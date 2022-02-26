import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import gsflow


class NetFlux(object):

    def __init__(self, f, precision='single', start_date="1-1-1970"):
        self.file = f
        self.header = [('kstp', '<i4'), ('kper', '<i4'), ('text', 'S16'),
                       ('ncol', '<i4'), ('nrow','<i4'), ('nlay', "<i4"),
                       ('imeth', '<i4'), ('delt', 'f4'), ('totim', 'f4'),
                       ('pertim', 'f4')]
        self.precision = precision
        if self.precision == 'single':
            self.realtype = np.float32
        else:
            self.realtype = np.float64
        m, d, y = [int(i) for i in start_date.split("-")]
        self.start_date = dt.datetime(y, m , d) - dt.timedelta(seconds=1)
        self._data = {}
        self._bydate = {}

        self.read_file()

    @property
    def data(self):
        """
        Gets a dictionary of data by (kper, kstp)
        """
        return self._data

    def read_file(self):
        with open(self.file, 'rb') as foo:
            foo.seek(0, 2)
            totalnbytes = foo.tell()
            foo.seek(0, 0)
            nbytes = foo.tell()
            date0 = self.start_date

            while nbytes < totalnbytes:
                header = self.binaryread(foo, self.header)
                nrow = int(header['nrow'][0])
                ncol = int(header['ncol'][0])
                kstp = int(header['kstp'][0])
                kper = int(header['kper'][0])

                shp = (nrow, ncol)
                array = self.binaryread(foo, self.realtype, shape=shp)

                if (kper, kstp) in self._data:
                    if self._data[(kper, kstp)].shape[0] == 2:
                        tarr = list(self._data[(kper, kstp)])
                        tarr = list(tarr)
                        tarr.append(array)
                    else:
                        tarr = list(tarr)
                        tarr.append(array)

                    array = np.array(tarr)

                self._data[(kper, kstp)] = array
                nbytes = foo.tell()

    @staticmethod
    def binaryread(file, vartype, shape=(1,), charlen=16):
        """
        Uses numpy to read from binary file.  This was found to be faster than the
            struct approach and is used as the default.

        """

        # read a string variable of length charlen
        if vartype == str:
            result = file.read(charlen * 1)
        else:
            # find the number of values
            nval = np.prod(shape)
            result = np.fromfile(file, vartype, nval)
            if nval == 1:
                result = result  # [0]
            else:
                result = np.reshape(result, shape)
        return result


if __name__ == "__main__":

    # set workspaces
    script_ws = os.path.abspath(os.path.dirname(__file__))
    repo_ws = os.path.join(script_ws, "..", "..")

    # set file paths
    file_path_recharge = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", "modflow", "output", "uzf_recharge.out")
    file_path_discharge = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", "modflow", "output", "uzf_discharge.out")
    file_path_mf_name_file = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", "windows", "rr_tr.nam")

    # load transient modflow model
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(file_path_mf_name_file),
                                       model_ws=os.path.dirname(file_path_mf_name_file),
                                       verbose=True, forgive=False, version="mfnwt",
                                        load_only=["BAS6", "DIS", "UZF", "UPW"])





    # RECHARGE: average over all stress periods ---------------------------------------------####

    # read in and extract recharge
    data = NetFlux(file_path_recharge)
    data = data.data

    # average recharge over all stress periods
    data = list(data.values())
    data = np.stack(data, axis=0)
    data = np.average(data, axis=0)

    # identify upland areas in the modeling domain
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    # plt.imshow(iuzfbnd)
    # plt.colorbar()
    # plt.title("IUZFBND")

    # identify upland areas with and without recharge
    recharge_upland_mask = (data > 0) & (iuzfbnd > 2)
    no_recharge_upland_mask = (data == 0) & (iuzfbnd > 2)

    # get SY
    sy = mf_tr.upw.sy.array

    # get VKS
    vks = mf_tr.uzf.vks.array

    # plot SY everywhere
    #plt.imshow(sy[0,:,:])

    # plot VKS everywhere within the watershed boundaries
    plt.figure(figsize=(6, 8), dpi=150)
    vks_masked = np.copy(vks)
    vks_masked[vks_masked == 0] = np.nan
    plt.imshow(vks_masked, norm=LogNorm())
    plt.colorbar()
    plt.title("VKS everywhere")
    file_name = 'vks_everywhere.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", file_name)
    plt.savefig(file_path)

    # plot SY for masked areas
    # not needed because it's a constant value everywhere

    # plot VKS for areas with recharge in the uplands
    plt.figure(figsize=(6, 8), dpi=150)
    vks_masked_recharge = np.copy(vks)
    vks_masked_recharge[np.invert(recharge_upland_mask)] = np.nan
    plt.imshow(vks_masked_recharge, norm=LogNorm())
    plt.colorbar()
    plt.title("VKS in areas with recharge in the uplands")
    file_name = 'vks_uplands_recharge.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", file_name)
    plt.savefig(file_path)


    # plot VKS for areas with no recharge in the uplands
    plt.figure(figsize=(6, 8), dpi=150)
    vks_masked_no_recharge = np.copy(vks)
    vks_masked_no_recharge[np.invert(no_recharge_upland_mask)] = np.nan
    plt.imshow(vks_masked_no_recharge, norm=LogNorm())
    plt.colorbar()
    plt.title("VKS in areas without recharge in the uplands")
    file_name = 'vks_uplands_no_recharge.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "archive", "20220223_01", file_name)
    plt.savefig(file_path)




