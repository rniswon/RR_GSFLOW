import numpy as np
import pandas as pd

def find_adjacent_zones(zones):
    """
    Given a 2D array of zones, this function returns a dictionary mapping each
    zone identifier to a set of adjacent zone identifiers, taking both row and
    column adjacency into account.

    Args:
        zones (numpy.ndarray): A 2D NumPy array of zone identifiers.

    Returns:
        A dictionary mapping zone identifiers to sets of adjacent zone identifiers.
    """
    adjacency_dict = {}
    for zone in np.unique(zones):
        if np.isnan(zone):
            continue
        adjacency_dict[zone] = set()
        rows, cols = np.where(zones == zone)
        for row, col in zip(rows, cols):
            for i in range(max(0, row - 1), min(zones.shape[0], row + 2)):
                for j in range(max(0, col - 1), min(zones.shape[1], col + 2)):
                    if i != row or j != col:
                        if zones[i, j] != zone:
                            if not(np.isnan(zones[i, j])):
                                adjacency_dict[zone].add(zones[i, j])
    return adjacency_dict


def aggregate_adjacent_zones(zones, max_size, exclude_zone = []):
    """
    Given a 2D array of zones and a maximum size for merged zones, this function returns a NumPy array where adjacent zones
    have been merged such that the merged zone has a number of cells less than or equal to max_size. The function also
    returns a dictionary mapping each original zone identifier to the identifier of the merged zone it belongs to.

    Args:
        zones (numpy.ndarray): A 2D NumPy array of zone identifiers.
        max_size (int): The maximum number of cells that a merged zone can have.

    Returns:
        A tuple of two values:
        - The merged NumPy array where adjacent zones have been merged.
        - A dictionary mapping original zone identifiers to merged zone identifiers.
    """
    zones_ = 1.0 * zones.copy()
    if len(exclude_zone)>0:
        mask = np.isin(zones_, exclude_zone)
        zones_[mask] = np.nan

    adjacency_dict = find_adjacent_zones(zones_)
    merged_zone = np.zeros_like(zones_)

    zone_set = set(adjacency_dict.keys())
    new_zone_id = 0
    nextzone = []
    while len(zone_set)>0:
        if len(nextzone)>0:
            zone = nextzone[0]
        else:
            zone = zone_set.pop()

        ncells = np.sum(zones_ == zone)
        batch = {zone}



        adj_zones = adjacency_dict[zone]
        adj_zones = adj_zones.intersection(zone_set)


        for z in adj_zones:
            nc = np.sum(zones_==z)
            if (ncells + nc )<= max_size:
                batch = batch.union({z})
                ncells = ncells + nc
            break

        new_zone_id = new_zone_id + 1
        for b in batch:
            merged_zone[zones_ == b] = new_zone_id

        zone_set = zone_set.difference(batch)
        batch = batch.difference({zone})
        adj_zones = adj_zones.difference(batch)

        nextzone = []
        if len(adj_zones)>0:
            nextzone = [adj_zones.pop()]


    return merged_zone


def aggregate_cascading_subb(zones, ):
    pass

def get_ag_fields(ag_file):

    fidr = open(ag_file, 'r')
    content = fidr.readlines()
    fidr.close()

    flg_in_stress_period = False
    line_counter = -1
    irr_data = []
    while True:
        line_counter = line_counter + 1
        if line_counter >= len(content):
            break
        line = content[line_counter]

        if "STRESS PERIOD" in line:
            if (line.strip())[0] == "#":
                continue
            flg_in_stress_period = True

            # get stress period number
            sp = int(line.strip().split()[2])
            continue

        if not (flg_in_stress_period):
            continue

        # if you are here, then you are inside a stress period
        type_of_irrigation = line.strip()

        if type_of_irrigation == "IRRWELL":
            line_counter = line_counter + 1
            line = content[line_counter]

            nwells = int(line.strip())

            for iwell in range(1, nwells + 1):
                line_counter = line_counter + 1
                line = content[line_counter]

                parts = line.strip().split()
                well_id = int(parts[0])
                ncell = int(parts[1])

                for i in range(ncell):
                    line_counter = line_counter + 1
                    line = content[line_counter]

                    parts = line.strip().split()
                    hru_i = int(parts[0])

                    irr_data.append([type_of_irrigation, sp, well_id, hru_i])

            line_counter = line_counter + 1
            line = content[line_counter]
            print("Stress Period {}".format(sp))
            if "END" in line:
                flg_in_stress_period = False
                continue
            elif line.strip() in ['IRRDIVERSION', 'IRRWELL',  'IRRPOND', 'SUPWELL']:
                line_counter = line_counter -1
                continue
            else:
                raise ValueError("Something is wrong. This line must contain 'END' keyword ")

        elif type_of_irrigation == "IRRDIVERSION":
            line_counter = line_counter + 1
            line = content[line_counter]
            n_diversions = int(line.strip())
            for ipod in range(1, n_diversions + 1):
                line_counter = line_counter + 1
                line = content[line_counter]

                parts = line.strip().split()
                seg_id = int(parts[0])
                ncell = int(parts[1])

                for i in range(ncell):
                    line_counter = line_counter + 1
                    line = content[line_counter]

                    parts = line.strip().split()
                    hru_i = int(parts[0])

                    irr_data.append([type_of_irrigation, sp, seg_id, hru_i])

            line_counter = line_counter + 1
            line = content[line_counter]
            print("Stress Period {}".format(sp))
            if "END" in line:
                flg_in_stress_period = False
                continue
            elif line.strip() in ['IRRDIVERSION', 'IRRWELL',  'IRRPOND', 'SUPWELL']:
                line_counter = line_counter -1
                continue
            else:
                raise ValueError("Something is wrong. This line must contain 'END' keyword ")


        elif type_of_irrigation == "SUPWELL":
            """
            Not Ready... it will generate error if data is different
            from zero
            """
            line_counter = line_counter + 1
            line = content[line_counter]

            if int(line.strip()) == 0:
                continue


        elif type_of_irrigation == "IRRPOND":
            line_counter = line_counter + 1
            line = content[line_counter]
            n_diversions = int(line.strip())
            for ipod in range(1, n_diversions + 1):
                line_counter = line_counter + 1
                line = content[line_counter]

                parts = line.strip().split()
                seg_id = int(parts[0])
                ncell = int(parts[1])

                for i in range(ncell):
                    line_counter = line_counter + 1
                    line = content[line_counter]

                    parts = line.strip().split()
                    hru_i = int(parts[0])

                    irr_data.append([type_of_irrigation, sp, seg_id, hru_i])

            line_counter = line_counter + 1
            line = content[line_counter]
            print("Stress Period {}".format(sp))
            if "END" in line:
                flg_in_stress_period = False
                continue
            elif line.strip() in ['IRRDIVERSION', 'IRRWELL', 'IRRPOND', 'SUPWELL']:
                line_counter = line_counter - 1
                continue
            else:
                raise ValueError("Something is wrong. This line must contain 'END' keyword ")

            pass

    return pd.DataFrame(irr_data, columns = ['irr_type', 'stress_period', 'element_id', 'field_hru'])




