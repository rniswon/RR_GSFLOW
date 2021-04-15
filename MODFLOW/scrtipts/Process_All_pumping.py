import Pumping_Analysis_Main
import filling_gaps
import filling_gaps_generate_final_dataset
import Water_use_source
import Generate_well_file
#--------------------------------
# Generate a csv file that holds data available pumping data,
#  temperture, and population
#--------------------------------
if False:
    Pumping_Analysis_Main.main()

# ------------------------------
# test filling perfromance using diffrent methods/partitions
# -----------------------------
if False:
    filling_gaps.run_test()

# ------------------------------
# now use all data to train the final regression model and fill the gaps
# ------------------------------
if False:
    filling_gaps_generate_final_dataset.run()

# ------------------------------
# add the source of water (SW/GW)
# ------------------------------
if True:
    Water_use_source.main()

# ------------------------
# find pumping per well
# ------------------------
Generate_well_file.main()


# ------- Sum water use at each diversion point
xx = 1