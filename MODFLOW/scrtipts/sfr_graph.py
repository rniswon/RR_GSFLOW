import os, sys
import pandas as pd
import networkx as nx

# compute a graph from shp_hru
def graph_from_sfr(sfr):
    """
    :param
    sfr is a pandas dataframe with at least the following columns ['ISEG', 'OUTSEG', 'IUPSEG']
    :return:
    """

    # get all segments
    net = nx.DiGraph()
    segments = sfr[sfr['ISEG']>0]
    segments = segments.sort_values(by = ['ISEG'])
    nodes = []
    for i, seg in segments.iterrows():
        if len(nodes) == 0:
            up_node = 1
            dn_node = 2
        else:

        net.add_edge(up_node,dn_node, segment_id = seg.ISEG)


        pass

    pass

def sfr_from_graph():

    pass


def get_upstream_segs(sfr, iseg):
    seg_path = []
    seg_path.pop(iseg)
    def _get_adj_up(sfr, iseg):
        upseg = sfr[sfr['OUTSEG'] == iseg]['ISEG']
        upseg = upseg.unique().tolist()

    curr_up = _get_adj_up(sfr, iseg)
    wait_list = curr_up
    for ups in wait_list:
        while True:
            seg_path.append(ups)
            next_seg = _get_adj_up(sfr, ups)
            if len(next_seg) == 0:
                break
            wait_list = wait_list + next_seg[1:]



