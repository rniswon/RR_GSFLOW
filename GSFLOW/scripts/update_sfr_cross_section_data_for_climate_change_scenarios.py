import os
import sys
import pandas as pd
import flopy
import gsflow

#---- Settings -------------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
input_ws = os.path.join(script_ws, "inputs_for_scripts", "gsflow_climate_change")           # input workspace
output_ws = os.path.join(script_ws, "script_outputs", "gsflow_climate_change_updated")       # output workspace

# set modflow name file
mf_name_file = os.path.join(input_ws, "rr_CanESM2_rcp45_heavy.nam")

# set constants
tabfile_maxval = 40177


#---- Read in -------------------------------------------------------####

mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    load_only=["BAS6", "DIS", "SFR"],
                                    verbose=True, forgive=False, version="mfnwt")
sfr = mf.sfr


#---- Update -------------------------------------------------------####

# loop through segments
seg_data = pd.DataFrame(sfr.segment_data[0])

# get segments with channel flow data
channel_flow_data = sfr.channel_flow_data[0]
segs_with_channel_flow_data = list(channel_flow_data.keys())

# loop through segs with channel flow data and update channel flow data
for seg in segs_with_channel_flow_data:

    # get NSTRPTS for this segment
    mask = seg_data['nseg'] == seg
    nstrpts = seg_data.loc[mask, 'nstrpts'].iloc[0]

    # set number of new values to generate
    total_num_val = 50
    num_new_val = total_num_val - nstrpts

    # update NSTRPTS for this segment
    seg_data.loc[mask, 'nstrpts'] = total_num_val

    # get channel flow data for this seg
    cfd = channel_flow_data[seg]
    flow = cfd[0]
    depth = cfd[1]
    width = cfd[2]

    # place in pandas data frame and get velocity at i=40
    df = pd.DataFrame({'flow': flow, 'depth': depth, 'width': width})
    df['area'] = df['depth'] * df['width']
    df['velocity'] = df['flow'] / df['area']
    velocity_t40 = df['velocity'].iloc[-1]

    # update flow
    flow_mult_factor = 1.1
    for val in list(range(num_new_val)):
        last_flow_val = flow[-1]
        new_flow_val = last_flow_val * flow_mult_factor
        flow.append(new_flow_val)

    # update depth
    additional_depth = 0.55
    for val in list(range(num_new_val)):
        last_depth_val = depth[-1]
        new_depth_val = last_depth_val + additional_depth
        depth.append(new_depth_val)

    # update width
    for idx in list(range(nstrpts, total_num_val)):
        new_width_val = flow[idx] / (velocity_t40 * depth[idx])
        width.append(new_width_val)

    # update channel flow data
    cfd[0] = flow
    cfd[1] = depth
    cfd[2] = width
    channel_flow_data[seg] = cfd


# update channel flow data
mf.sfr.channel_flow_data[0] = channel_flow_data

# update segment data
mf.sfr.segment_data[0] = seg_data.to_records(index=False)

# update sfr maxval which for some reason is output incorrectly if not set here
mf.sfr.maxval = tabfile_maxval

# update sfr tabfile numval which is incorrect for the climate change scenarios
tabfiles_dict = sfr.tabfiles_dict
segs_with_tabfiles = list(tabfiles_dict.keys())
for seg in segs_with_tabfiles:
    tabfiles_dict[seg]['numval'] = tabfile_maxval
mf.sfr.tabfiles_dict = tabfiles_dict

# write sfr file
mf.sfr.fn_path = os.path.join(output_ws, "rr_climate.sfr")
mf.sfr.write_file()