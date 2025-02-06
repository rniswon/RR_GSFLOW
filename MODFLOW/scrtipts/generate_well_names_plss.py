from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import split
import geopandas
import matplotlib.pyplot as plt
from shapely.ops import linemerge, unary_union, polygonize
import numpy as np

def splitPolygon(polygon, nx, ny, obs):
    bounds = polygon.bounds
    minx = bounds['minx'].values[0]
    maxx = bounds['maxx'].values[0]
    maxy = bounds['maxy'].values[0]
    miny = bounds['miny'].values[0]
    dx = (maxx - minx) / nx
    dy = (maxy - miny) / ny
    r1 = ['a', 'b', 'c', 'd']
    r1.reverse()
    r2 = ['m', 'l', 'k', 'j']

    qq = np.array([r1, ['e', 'f', 'g', 'h'], r2, ['n', 'p', 'q', 'r']])
    qq = np.flipud(qq)

    horizontal_splitters = [LineString([(minx, miny + i * dy), (maxx, miny + i * dy)]) for i in range(ny)]
    vertical_splitters = [LineString([(minx + i * dx, miny), (minx + i * dx, maxy)]) for i in range(nx)]
    splitters = horizontal_splitters + vertical_splitters
    result = polygon.geometry.values[0]

    for splitter in splitters:
        result = MultiPolygon(split(result, splitter))
    plot_results = True
    lines = unary_union(linemerge([geom.exterior for shape in result for geom in result.geoms]))
    result = list(polygonize(lines))

    qq_keys = {}
    for i in range(16):
        x = result[i].centroid.x
        y = result[i].centroid.y
        col = int(abs((x - minx)/dx))
        row = int(abs((y - miny) / dy))
        qq_keys[i] = qq[row, col]

        if plot_results:
            plt.plot(result[i].exterior.xy[0], result[i].exterior.xy[1])
            plt.text(x,y,qq[row, col])
    if plot_results:
        obs.plot(ax=plt.gca(), color='k')

    qqs = []
    for w in obs.geometry.values:
        current_qq = ''
        for i in range(16):
            if w.within(result[i]):
                current_qq = qq_keys[i]
                break
        qqs.append(current_qq)

    return qqs


if __name__ == "__main__":
    sections_shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\plss_sections.shp")
    obs_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\FINAL_All_RR_WL_wells_merge_non_near_and_near_master_sites_no_dupes.shp"
    obs_df = geopandas.read_file(obs_file)
    obs_df = obs_df.to_crs({'init': 'epsg:26910'})
    sections_shp = sections_shp.to_crs({'init': 'epsg:26910'})

    join_df = geopandas.sjoin(obs_df, sections_shp, how = 'inner')
    join_df['WNAME'] = ''
    ccount = 0
    lengdf = len(join_df)
    for iobs, obs in join_df.iterrows():
        print((100.0*ccount)/lengdf)
        ccount = ccount + 1
        section_poly = sections_shp.loc[sections_shp['OBJECTID'] == obs['OBJECTID'], 'geometry' ]
        w_points = join_df.loc[join_df['OBJECTID'] == obs['OBJECTID'], 'geometry']
        qqs = splitPolygon(section_poly, 4, 4, w_points)
        rangeC = join_df.loc[join_df['OBJECTID'] == obs['OBJECTID'], ['Range']]
        rangeC = rangeC.copy()
        rangeC = rangeC['Range'].str.replace("R", "").values

        tw = join_df.loc[join_df['OBJECTID'] == obs['OBJECTID'], ['Township']]
        tw = tw.copy()
        tw = tw['Township'].str.replace("T", "").values

        sections = join_df.loc[join_df['OBJECTID'] == obs['OBJECTID'], ['Section']].values

        final_names = []
        for iii, sec in enumerate(sections):
            wn = rangeC[iii] + "/" + tw[iii] + "-"+ str(sections[iii][0])+ qqs[iii].upper()
            final_names.append(wn)

        join_df.loc[join_df['OBJECTID'] == obs['OBJECTID'], ['WNAME']] = final_names

        xx = 1




    xx = 1