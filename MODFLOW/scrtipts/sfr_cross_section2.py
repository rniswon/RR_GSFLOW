import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union
import datetime
from matplotlib.backends.backend_pdf import PdfPages
def main():
    cross_section_folder = r"D:\Workspace\projects\RussianRiver\modflow\other_files\main_cross_sections"
    RR_cs = Cross_section()
    RR_cs.cross_section_folder = cross_section_folder
    RR_cs.compute()
    RR_cs.calc_average_curve()



class Cross_section(object):
    def __init__(self):
        self.cross_section_folder = ''
        self.n_increment = 40
        self.debug_plots = True

    def compute(self):
        files = os.listdir(self.cross_section_folder)
        tab_info = []
        with PdfPages('all_tab_files.pdf') as pdf:
            for file in files:
                fn = os.path.join(self.cross_section_folder, file)
                table = np.loadtxt(fn, skiprows=1)

                if file[0] in ['s', 'p', 'S', 'P']:
                    # this segments is either for sonoma or potter valley
                    parts = file.split("_")
                    stem = parts[0].upper()
                    id = int(parts[1])
                    segid = int(parts[2].split(".")[0])

                else:
                    parts = file.split("_")
                    stem = 'm'.upper() # main stem
                    id = int(parts[0])
                    segid = int(parts[1].split(".")[0])
                Table_dpth_area = self.flow_geom2(table, file, id, stem)
                tab_info.append([stem, id, segid, Table_dpth_area, file])
                pdf.savefig()
                plt.close()
        self.tab_info = tab_info

    def calc_average_curve(self):
        stems = [sstem[0] for sstem in self.tab_info]
        ids = [id[1] for id in self.tab_info]
        stems = np.array(stems)
        ids = np.array(ids)
        stem_nms = np.unique(stems)
        curr_stem = []
        final_cross_section = {}
        for st in stem_nms:
            # get all info about current stem
            curr_stem = []
            for row in self.tab_info:
                if row[0]==st:
                    curr_stem.append(row)
            ##
            curr_stem.sort(key=lambda x: x[1])
            for i in range(len(curr_stem)-1):
                print(i)
                up_section = curr_stem[i]
                dn_section = curr_stem[i+1]
                # get the similiar table size
                min_l = min(len(up_section[3]), len(dn_section[3]))
                up_section[3] = up_section[3][0:min_l]
                dn_section[3] = dn_section[3][0:min_l]
                ave_tab = []
                seg_id = dn_section[2]
                for col in up_section[3].columns:
                    curr = 0.5 * up_section[3][col].values + 0.5 * dn_section[3][col].values
                    ave_tab.append(curr)
                final_cross_section[seg_id] = pd.DataFrame(np.array(ave_tab).T, columns=up_section[3].columns)
        pass

        np.save('sfr_flow_depth_tabs.npy', final_cross_section )

    def create_polygon(self, x, z):
        ls = LineString(np.c_[x, z])
        lr = LineString(ls.coords[:] + ls.coords[0:1])
        mls = unary_union(lr)
        cs = MultiPolygon(list(polygonize(mls)))
        return cs

    def remove_tiny_poy(self, cs):
        big_area = 0
        if cs.geom_type == 'MultiPolygon':
            for c_ in cs:
                if c_.area > big_area:
                    big_area = c_.area
                    pol_cs = c_
            return pol_cs
        else:
            return cs

    def calc_geom(self, ps, maxz):

        if ps.geom_type == 'MultiPolygon':
            width = 0.0
            wetted = 0.0
            area = 0.0
            depths = []
            for pss in ps:
                area = area + pss.area
                curr_width =  np.max(pss.exterior.xy[0]) - np.min(pss.exterior.xy[0])
                width = width + curr_width
                wetted = wetted + (pss.length - curr_width)
                depths = depths + (maxz - pss.exterior.coords.xy[1]).tolist()
            depths = np.array(depths)

        else:
            area = ps.area
            width = np.max(ps.exterior.xy[0]) - np.min(ps.exterior.xy[0])
            wetted = (ps.length - width)
            depths = maxz - ps.exterior.coords.xy[1]

        depths[depths <= 0] = np.nan
        av_depth = np.nanmean(depths)
        max_depth = np.nanmax(depths)
        hraduis = area / wetted
        return area, max_depth, av_depth, wetted, hraduis, width


    def flow_geom2(self, table, file, id, stem):
        Debug_flag = True
        x = table[:, 0]
        z = table[:, 1]

        if id >= 24 or stem.upper()=='S':
            z = z * 0.3048
            pass


        # sort the data based on x
        order = np.argsort(x)
        x = x[order]
        z = z[order]

        # remove any data farther than 150 meter from the lowest point
        diffX = x - x[np.argmin(z)]
        if not(id == 74):
            mask = np.logical_and(diffX >= -150, diffX <= 150)
            x = x[mask]
            z = z[mask]
        # find side of maximum  elevations
        side_sign = x[np.argmax(z)] - x[np.argmin(z)]
        if side_sign>=0:
            # high elevation on the right, check the left for a max z
            minz_x = x[np.argmin(z)]
            maxz_2 = max(z[x<=minz_x])
        else:
            # highest elevation on left
            minz_x = x[np.argmin(z)]
            maxz_2 = max(z[x >= minz_x])


        # data bounds
        x_max = np.max(x)
        x_min = np.min(x)
        zmin = np.min(z)
        zmax = maxz_2
        loc = z >= maxz_2
        z[loc] = maxz_2
        z[0] = maxz_2
        z[-1] =  maxz_2
        self.z_increment = (maxz_2 - zmin) / float(self.n_increment)
        # remove points above zmax
        #loc = z <=zmax
        #z = z[loc]
        #x = x[loc]
        #self.z_increment = (zmax - zmin) / float(self.n_increment)


        # generate ploygon
        cross_sc_poly = self.create_polygon(x, z)
        if False:
            ax = plt.figure().gca()
            self.plot_shaply(cross_sc_poly, ax, 'g')

        # remove tiny polygons
        if 1:
            cross_sc_poly = self.remove_tiny_poy(cross_sc_poly)
            #x = np.array(cross_sc_poly.exterior.coords.xy[0])
            #z = np.array(cross_sc_poly.exterior.coords.xy[1])

            #x = x[loc]
            #cross_sc_poly = self.create_polygon(x, z)

        if Debug_flag:

            ax = plt.figure().gca()
            plt.title(file)
            self.plot_shaply(cross_sc_poly, ax, 'r')

        curr_z = zmin + self.z_increment
        geom_info = []
        PreviousWidth = 0
        while curr_z <= zmax:
            water_table = Polygon([(x_min, zmin), (x_min, curr_z), (x_max, curr_z), (x_max, zmin)])
            ps = cross_sc_poly.intersection(water_table)
            self.plot_shaply(ps, ax, 'b')
            if not ps.is_empty:
                if 0:
                    ps = self.remove_tiny_poy(ps)
                self.plot_shaply(ps, ax, 'b')
                # compute average area, max depth, wetted perm
                area, max_depth, av_depth, wetted, hraduis, width = self.calc_geom(ps, curr_z)

                geom_info.append([area, max_depth, av_depth, wetted, hraduis, width])
            else:
                print('No intersection is found....')



            curr_z = curr_z + self.z_increment

        geom_df = pd.DataFrame(geom_info, columns=['area', 'max_depth', 'av_depth', 'wetted', 'hraduis', 'width'])
        return geom_df




        pass

    def flow_geom(self, table):
        x = table[:,0]
        z = table[:,1]

        x_max = np.max(x)
        x_min = np.min(x)

        # minimum z
        zmin = np.min(z)
        zmax = np.max(z)
        self.z_increment = (zmax - zmin)/float(self.n_increment)

        #
        ls = LineString(np.c_[x, z])
        lr = LineString(ls.coords[:] + ls.coords[0:1])
        mls = unary_union(lr)
        cs = MultiPolygon(list(polygonize(mls)))
        #
        big_area = 0
        if cs.geom_type == 'MultiPolygon':
            for c_ in cs:
                if c_.area > big_area:
                    big_area = c_.area
                    pol_cs = c_

        cs = pol_cs
        curr_z = zmin + self.z_increment
        ax = plt.figure().gca()
        ax2 = plt.figure().gca()
        dpth_area = []
        while curr_z <= zmax:
            water_table = Polygon([(x_min,zmin), (x_min,curr_z), (x_max,curr_z), (x_max, zmin)])
            ps = cs.intersection(water_table)
            if not ps.is_empty:
                if ps.geom_type == 'MultiPolygon':
                    avdepth = []
                    area = []
                    for pp in ps:
                        if zmin in pp.exterior.coords.xy[1]:
                            # check for wrong water table
                            min_x_ = min(pp.exterior.coords.xy[0])
                            max_x_ = max(pp.exterior.coords.xy[0])
                            zmin1 = pp.exterior.coords.xy[1][pp.exterior.coords.xy[0] == min_x_]
                            zmin2 = pp.exterior.coords.xy[1][pp.exterior.coords.xy[0] == max_x_]
                            min_z_ = min(zmin1, zmin2)
                            rec = Polygon([(min_x_,min_z_), (min_x_,min_z_), (max_x_,min_z_), (max_x_, min_z_)])
                            pp = pp.intersection(rec)
                            self.plot_shaply(pp, ax2, 'r')
                            big_area = 0
                            if pp.geom_type == 'MultiPolygon':
                                for c_ in pp:
                                    if c_.area > big_area:
                                        big_area = c_.area
                                        pol_cs2 = c_
                                pp = pol_cs2
                            depths = curr_z - pp.exterior.coords.xy[1]
                            depths[depths<=0] = np.nan
                            avdepth = np.nanmean(depths)
                            area = pp.area
                            width = np.max(pp.exterior.xy[0]) - np.min(pp.exterior.xy[0])
                            HRaduis = area / (pp.length - width)
                            pol_to_plot = pp
                            break
                        else:
                            pass # just for debuging
                    area = np.array(area)
                    avdepth = np.array(avdepth)
                    avdepth = (area * avdepth)/np.sum(area)
                    area = np.sum(area)

                else:
                    min_x_ = min(ps.exterior.coords.xy[0])
                    max_x_ = max(ps.exterior.coords.xy[0])
                    zmin1 = ps.exterior.coords.xy[1][ps.exterior.coords.xy[0] == min_x_]
                    zmin2 = ps.exterior.coords.xy[1][ps.exterior.coords.xy[0] == max_x_]
                    min_z_ = min(zmin1, zmin2)
                    rec = Polygon([(min_x_, min_z_), (min_x_, min_z_), (max_x_, min_z_), (max_x_, min_z_)])
                    ps = ps.intersection(rec)
                    self.plot_shaply(ps, ax2, 'r')
                    big_area = 0
                    if ps.geom_type == 'MultiPolygon':
                        for c_ in ps:
                            if c_.area > big_area:
                                big_area = c_.area
                                pol_cs2 = c_
                        ps = pol_cs2
                    depths = curr_z - ps.exterior.coords.xy[1]
                    depths[depths <= 0] = np.nan
                    avdepth = np.nanmean(depths)
                    area = ps.area
                    width = np.max(ps.exterior.xy[0]) - np.min(ps.exterior.xy[0])
                    HRaduis = area/(ps.length - width)
                    pol_to_plot = ps

                dpth_area .append([avdepth, area, HRaduis])

                if self.debug_plots:
                    #self.plot_shaply(water_table, ax, 'b')
                    #self.plot_shaply(cs, ax, 'r')
                    self.plot_shaply(pol_to_plot, ax,'g')
            curr_z = curr_z + self.z_increment

        dpth_area = pd.DataFrame(dpth_area, columns=['depth','area', 'h_raduis'])
        return dpth_area


    def plot_shaply(self,obj, ax, color):

        if obj.geom_type == 'LineString':
            ax.plot(obj.coords.xy[0], obj.coords.xy[1], color = color)

        if obj.geom_type =='MultiPoint':
            xy = self.get_coordinates(obj)
            ax.scatter(xy[:,0], xy[:,1])
        if obj.geom_type == 'MultiPolygon':
            for o in obj:
                x, y = o.exterior.xy
                ax.plot(x, y, color=color, alpha=0.7,
                        zorder=2)
        if obj.geom_type == 'Polygon':
            x, y = obj.exterior.xy
            ax.plot(x, y, color=color, alpha=0.7, zorder=2)


    def get_coordinates(self, obj):
        return np.array([[o.x, o.y] for o in obj])


def plot_tab_info():

    cross_section = np.load('sfr_flow_depth_tabs.npy')
    cross_section = cross_section.all()
    with PdfPages('all_tab_files2.pdf') as pdf:
        for seg in cross_section.keys():
            curr_info = cross_section[seg]
            fig = plt.figure()

            col = ['area', 'max_depth', 'av_depth', 'wetted', 'hraduis', 'width']
            plt.subplot(2,2,1)
            plt.title(str(seg))
            try:
                plt.plot(curr_info['max_depth'], curr_info['area'] )
            except:
                pass
            plt.xlabel('Max. Depth (m)')
            plt.ylabel('Area')

            plt.subplot(2, 2, 2)
            plt.plot(curr_info['max_depth'], curr_info['wetted'])
            plt.xlabel('Max. Depth (m)')
            plt.ylabel('wetted')
            plt.subplot(2, 2, 3)
            plt.plot(curr_info['max_depth'], curr_info['hraduis'])
            plt.xlabel('Max. Depth (m)')
            plt.ylabel('H. Raduis')
            plt.subplot(2, 2, 4)
            plt.plot(curr_info['max_depth'], curr_info['width'])
            plt.xlabel('Max. Depth (m)')
            plt.ylabel('Width')
            plt.tight_layout()


            pdf.savefig(fig)  # or you can pass a Figure object to pdf.savefig
            plt.close()
            pass

    pass

if __name__ == "__main__":
    if True:
        main()
    if True:
        plot_tab_info()

    pass


