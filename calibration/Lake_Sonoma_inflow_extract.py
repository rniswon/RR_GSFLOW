import urllib2
from calendar import monthrange

# This script extracts daily 'mean inflow' values in cfs for Lake Sonoma from the U.S. Army Corps of Engineers website
# Some of the monthly reports are not available. Values of -9999 are given for these days.
# Works for reports prior to October 2004. Inspect output as some reports are abbreviated or otherwise anomalous
# Author: John Engott 5/30/2018

error_out = 'C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\Lake_Sonoma_error.out'
output_file = 'C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\Lake_Sonoma_inflows_USACE.out'
fid = open(error_out, 'w')
monthlist = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
inflow_all = []
error = 0

for yr in range(1990, 2016, 1):         # enter appropriate year range
    for mo in monthlist:
        url = 'http://www.spk-wc.usace.army.mil/fcgi-bin/monthly.py?month=' + mo + '&year=' + str(yr) + '&project=wrs'

        page = urllib2.urlopen(url)
        page_content = page.read()
        try:
            table = page_content.split('(ac-ft)')[4]
            table = table.split('Totals')[0]
            table = table.split()
            inflow_month = [table[i] for i in range(4,len(table),13)]
            inflow_all.append(inflow_month)

        # if monthly report is not available, write -9999 to list and write month to file
        except:
            inflow_month = ['-9999' for j in range(0,monthrange(yr, monthlist.index(mo)+1)[1])]
            inflow_all.append(inflow_month)
            fid.write(mo)
            fid.write(' %i \n' %yr)
            error += 1
            pass
fid.close()

# combine list of monthly lists into a single flat list
inflow_flat = [item for sublist in inflow_all for item in sublist]

# write inflows to output file in a consecutive vertical list
fid2 = open(output_file, 'w')
fid2.write('USACE reported inflows to Lake Sonoma for 1990-2015 \n')
fid2.write('Number of missing months: %i (see error.out for list) \n' %error)
for item in range(len(inflow_flat)):
    fid2.write(inflow_flat[item])
    fid2.write('\n')
fid2.close

pass