import os, sys
import pandas as pd
from dbfpy import dbf
import numpy as np
#import shapefile as shp
import matplotlib.pylab as plt
#from descartes import PolygonPatch
#import arcpy
#import dbf as dbf2

"""
Author: Ayman Alzraiee
Date : 3/18/2017

"""
def get_attribute_table(shpfile):
    """
    :param att_table: dbf file from a gis shape file
    :return: panda data frame for the attribute table
    """
    base_file = os.path.dirname(shpfile)
    file_parts = os.path.basename(shpfile).split('.')
    del file_parts[-1]
    file_parts = '.'.join(file_parts)
	
    dbf_file = os.path.join(base_file, file_parts + ".dbf")


    db = dbf.Dbf(dbf_file)
    field_names = db.fieldNames
    db_data = []
    db_data = []
    db_data = [rec.fieldData for rec in db]
    df = pd.DataFrame(db_data,columns=field_names)
    db.close()
    return df

def add_field2 (shpfile,field_name, field_data):
    base_file = os.path.dirname(shpfile)
    file_parts = os.path.basename(shpfile).split('.')
    del file_parts[-1]
    file_parts = '.'.join(file_parts)
    dbf_file = os.path.join(base_file, file_parts + ".dbf")

    att = get_attribute_table(shpfile)
    att[field_name] = field_data
    att.to_csv('__temp__.csv')
    dbf2.from_csv('__temp__.csv', to_disk=True, filename=dbf_file)

    try:
        #dbf2.from_csv('__temp__.csv', dbf_file)
        dbf.from_csv('__temp__.csv', to_disk=True, filename=dbf_file)
    except:
        print "For some reason, cannot proudcue the same shapefile. A new file is genrated..."
        newdbf = os.path.join(base_file, file_parts+"_" + ".dbf")
        dbf2.from_csv('__temp__.csv',   'test.dbf')
        for file in  os.listdir(base_file):
            if file.endswith(".txt"):
                print(os.path.join("/mydir", file))

    xx = 1
        


    

def add_field (shpfile,field_name, field_data):
    """

    :param att_table:
    :return:
    """
    base_file = os.path.dirname(shpfile)
    file_parts = os.path.basename(shpfile).split('.')
    del file_parts[-1]
    file_parts = '.'.join(file_parts)

    dbf_file = os.path.join(base_file, file_parts + ".dbf")
##
    arcpy.env.workspace =   base_file

    # Set local variables
    inFeatures = shpfile
    fieldName1 = field_name
    fieldPrecision = 9
    fieldAlias = "refcode"
    fieldName2 = "status"
    fieldLength = 10

    # Execute AddField twice for two new fields
    try:
        arcpy.AddField_management(inFeatures, fieldName1, "DOUBLE", field_length=fieldLength )
    except:
        print " Close arcgis if it open, or choose a different name for the field"


    db = dbf.Dbf(dbf_file)
    i = 0
    for rec in db:
        rec[fieldName1]=field_data[i]
        rec.store()
        i += 1
    del rec
    db.close()
    xx = 1
        






def plot_shp_lines(shpfile, color,fig ):
    sf = shp.Reader(shpfile)
    for shape in sf.shapeRecords():

        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        x = np.array(x)
        y = np.array(y)
        try:
            ax = fig.gca()
        except:
            ax = fig
        parts = shape.shape.parts
        for ii in range(len(parts)):
            strr = parts[ii]
            try:
                edd = parts[ii+1]
                xx = x[strr:edd]
                yy = y[strr:edd]
            except:

                xx = x[strr:]
                yy = y[strr:]
            
            ax.plot(xx,yy, color=color, linewidth = 2)
            ax.axis('equal')
        

def plot_shp_points(shpfile, color , fig ):
    sf = shp.Reader(shpfile)
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        #plt.scatter(x,y, color=color)
        ax = fig.gca()
        ax.scatter(x,y, color=color)
        ax.axis('equal')
        fig.hold(True)


