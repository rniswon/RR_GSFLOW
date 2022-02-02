

# Read in -----------------------------------------------####

# read in well completion csv

# read in ag package and extract well list




# Reformat well completion data -----------------------------------------------####

# create data frame with only wells in mendocino and sonoma counties




# Reformat AG well list -----------------------------------------------####

# get lat/long for each well based on HRU cell center




#  Estimate well layer -----------------------------------------------####

# determine well distance cutoffs (maybe several cutoffs that are each tried in turn)

# loop through each AG well

    # get distance of AG well from all the well completion wells

    # if there is at least one well within the first distance cutoff

        # calculate the average well depth for wells within the cutoff

        # set the AG well depth equal to the calculated average

    # elif there is at least one well within the second distance cutoff

        # calculate the average well depth for wells within the cutoff

        # set the AG well depth equal to the calculated average

    # elif there is at least one well within the third distance cutoff

        # calculate the average well depth for wells within the cutoff

        # set the AG well depth equal to the calculated average

    # note: continue as necessary

    # calculate well elevation using elevation of the model grid cell containing the AG well

    # determine well layer


#  Export table of AG well layers -----------------------------------------------####

#TODO: use this table to update well layers in AG package in Main_gsflow.py