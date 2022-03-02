import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


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
    file_path_recharge = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "uzf_recharge.out")
    file_path_discharge = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "uzf_discharge.out")


    # RECHARGE: average over all stress periods ---------------------------------------------####

    # read in and extract recharge
    data = NetFlux(file_path_recharge)
    data = data.data

    # average recharge over all stress periods
    data = list(data.values())
    data = np.stack(data, axis=0)
    data = np.average(data, axis=0)

    # plot recharge
    data[data==0] = np.nan
    plt.figure(figsize=(6, 8), dpi=150)
    im = plt.imshow(data, norm=LogNorm())
    plt.colorbar(im)
    plt.title("UZF recharge net flux: averaged over all stress periods,\ngrid cells with recharge = 0 set to nan")
    file_name = 'netrech_all.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "uzf_netrech_netdis", file_name)
    plt.savefig(file_path)



    # RECHARGE: average over each month ---------------------------------------------####

    # read in and extract recharge
    data = NetFlux(file_path_recharge)
    data = data.data
    data = list(data.values())
    num_stress_period = len(data)
    data = np.stack(data, axis=0)

    # loop over months
    months = list(range(12))
    if num_stress_period < 12:
        months = [x for x in months if x < num_stress_period]
    sp = list(range(num_stress_period))
    for month in months:

        # generate month indices for this month
        month_idx = sp[month::12]

        # extract
        data_month = data[month_idx, :, :]

        # average
        data_month = np.average(data_month, axis=0)

        # plot recharge
        data_month[data_month==0] = np.nan
        plt.figure(figsize=(6, 8), dpi=150)
        im = plt.imshow(data_month, norm=LogNorm())
        plt.colorbar(im)
        plt.title("UZF recharge net flux: month " + str(month + 1) + "\ngrid cells with recharge = 0 set to nan")
        file_name = 'netrech_month_' + str(month+1) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "uzf_netrech_netdis", file_name)
        plt.savefig(file_path)



    # DISCHARGE: average over all stress periods ---------------------------------------------####

    # read in and extract discharge
    data = NetFlux(file_path_discharge)
    data = data.data

    # average discharge over all stress periods
    data = list(data.values())
    data = np.stack(data, axis=0)
    data = np.average(data, axis=0)

    # make positive so that can take log
    data = data * -1

    # plot discharge
    data[data==0] = np.nan
    plt.figure(figsize=(6, 8), dpi=150)
    im = plt.imshow(data, norm=LogNorm())
    plt.colorbar(im)
    plt.title("UZF discharge net flux: averaged over all stress periods,\ngrid cells with discharge = 0 set to nan")
    file_name = 'netdis_all.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "uzf_netrech_netdis", file_name)
    plt.savefig(file_path)



    # DISCHARGE: average over each month ---------------------------------------------####

    # read in and extract discharge
    data = NetFlux(file_path_discharge)
    data = data.data
    data = list(data.values())
    num_stress_period = len(data)
    data = np.stack(data, axis=0)

    # loop over months
    months = list(range(12))
    if num_stress_period < 12:
        months = [x for x in months if x < num_stress_period]
    sp = list(range(num_stress_period))
    for month in months:

        # generate month indices for this month
        month_idx = sp[month::12]

        # extract
        data_month = data[month_idx, :, :]

        # average
        data_month = np.average(data_month, axis=0)

        # make positive so that can take log
        data_month = data_month * -1

        # plot discharge
        data_month[data_month==0] = np.nan
        plt.figure(figsize=(6, 8), dpi=150)
        im = plt.imshow(data_month, norm=LogNorm())
        plt.colorbar(im)
        plt.title("UZF discharge net flux: month " + str(month + 1) + "\ngrid cells with discharge = 0 set to nan")
        file_name = 'netdis_month_' + str(month+1) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "uzf_netrech_netdis", file_name)
        plt.savefig(file_path)

    xx=1



