# flopy's MfListBudget module can be used to extract the percent discrepancy information from the list file


lst = MfListBudget("rr_tr.lst")
df_flux, df_vol = lst.get_dataframes(start_datetime="1-1-1970")
vals = df_flux["percent_discrepancy"].values