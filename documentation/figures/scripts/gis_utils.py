import os
import matplotlib.pyplot as plt
import geopandas
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib
from flopy.plot import styles

def model_rowcol_2_xy(mf, row, col):
    """
    convert row and col to real coordinates
    mf is modflow object that has a grid with epsg

    return x,y
    """
    grid = mf.modelgrid
    local_x = grid.get_xvertices_for_layer(0)
    local_y = grid.get_yvertices_for_layer(0)
    x = local_x[row, col]
    y = local_y[row, col]
    return x, y


def xy_to_shp(df, x_c, y_c, epsg):
    """
    convert a dataframe that has x and y coordinate to geopandas dataframe
    """
    geometry = geopandas.points_from_xy(df[x_c], df[y_c], crs=epsg)
    gdf = geopandas.GeoDataFrame(df, geometry=geometry)
    return gdf


def row_col_to_shp(df, mf, row_c, col_c, epsg):
    """
    convert a dataframe df with rows and col info to shapefile object

    """
    df_ = df.copy()
    x,y = model_rowcol_2_xy(mf, df_[row_c], df_[col_c])
    df_['geoX'] = x
    df_['geoY'] = y
    gdf = xy_to_shp(df_, x_c = 'geoX', y_c = 'geoY', epsg = epsg)

    return gdf


def plot_scatter_map(df, legend_column, cmap, title, figfile, log_scale = False,
                     proj_latlon = True, legend_kwds = {'label':'Average Pumping '} ):


    df_shp = df.copy()
    df_shp.to_crs(epsg=4326, inplace=True)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    if log_scale:
        norm = matplotlib.colors.LogNorm(vmin=df_shp[legend_column].min(), vmax=df_shp[legend_column].max())
    else:
        norm = None

    with styles.USGSMap():
        ax = df_shp.plot(ax = ax, column= legend_column, alpha=1, cmap=cmap, markersize=5, legend=True,
                        legend_kwds={'shrink': 0.6}, cax=cax, norm=norm)
        cx.add_basemap(ax, crs=df_shp.crs.to_string(), source=cx.providers.Stamen.TonerLines, alpha=1, attribution = False)
        cx.add_basemap(ax, crs=df_shp.crs.to_string(), source=cx.providers.Stamen.TonerBackground, alpha=0.1, attribution = False)

        styles.heading(ax=ax,
                       heading= title,
                       idx=0, fontsize=16)
        styles.xlabel(ax=ax, fontsize=16, label='LONG')
        styles.ylabel(ax=ax, fontsize=16, label='LAT')
        plt.tick_params(axis='x', labelsize=14)
        plt.tick_params(axis='y', labelsize=14)
        plt.savefig(figfile)
        plt.close(fig)




