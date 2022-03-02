# I wrote some code awhile back for FloPy that allows the user to get data in a pandas dataframe from zonebudget.
# You'll need to run zonebudget first.

# Here's a code snippet on how to get subbasin budget info using FloPy.
# You'll need to update the start_datetime="" parameter and change zbout
# to zvol in the last block if you want a budget representation that is in m3/kper.


from flopy.utils import ZoneBudget
import gsflow
import flopy
gsf = gsflow.load_from_file("rr_tr.control")
ml = gsf.mf
# can use net=True if you want a the net budget for plotting instead of in and out components
zbout = ZoneBudget.read_output("rr_tr.csv2.csv", net=True, dataframe=True, pivot=True, start_datetime="1-1-1970")
# zbout is a dataframe of flux values. m^3/d in your case. For a volumetric representation that covers
# the entire stress period (Note you must have cbc output for each stress period for this to be valid) use this
# hidden method. Returns m^3/kper.
zrec = zbout.to_records(index=False)
zvol = flopy.utils.zonbud._volumetric_flux(zrec, ml.modeltime, extrapolate_kper=True)
# now create a dataframe that corresponds to each zonebudget zone using either zvol (m3/kper) or zbout (m3/d)
zones = zbout.zone.unique()
sb_dfs = []
for zone in zones:
    tdf = zbout[zbout.zone == zone]
    tdf.reset_index(inplace=True, drop=True)
    sb_dfs.append(tdf)