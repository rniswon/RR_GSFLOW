import time
import os
import sys
import math




### CLASSES ###
class buildConn(object):
    def __init__(self, row, col, segID):
        self.row = row
        self.col = col
        if segID == 1:
            otRow, otCol = row - 1, col
        if segID == 2:
            otRow, otCol = row, col + 1
        if segID == 3:
            otRow, otCol = row + 1, col
        if segID == 4:
            otRow, otCol = row, col - 1

        self.otRow = otRow
        self.otCol = otCol

    def build(self):

        conn = tuple(reversed(sorted([(self.row, self.col), (self.otRow, self.otCol)])))
        self.conn = conn[0][0], conn[0][1], conn[1][0], conn[1][1]




### FUNCTIONS ###
def getAngles(xy1, xy2):
    x1, y1 = float(xy1[0]), float(xy1[1])
    x2, y2 = float(xy2[0]), float(xy2[1])
    dx, dy = (x2 - x1, y2 - y1)
    # math.degrees(math.atan(test)),
    mainAngle = 90 - math.degrees(math.atan2(dy, dx))
    if mainAngle < 0:
        mainAngle += 360
    retVal = [mainAngle]
    for i in range(1, 4):
        mainAngle += 90
        if mainAngle > 360:
            mainAngle -= 360
        retVal.append(mainAngle)
    return retVal


def checkBounds(row, col, numOfRows, numOfCols):
    if row == 0:
        return False
    elif row > numOfRows:
        return False
    elif col == 0:
        return False
    elif col > numOfCols:
        return False
    else:
        return True





def getPoint(angle, distance, startPoint):

    radAngle = math.radians(angle)
    x = startPoint[0] + (math.sin(radAngle) * distance)
    y = startPoint[1] + (math.cos(radAngle) * distance)

    return x, y


def getMax(inVal, newVal):
    if newVal > inVal:
        otVal = newVal
    else:
        otVal = inVal
    return otVal


def getMin(inVal, newVal):
    if newVal < inVal:
        otVal = newVal
    else:
        otVal = inVal
    return otVal



# import Arc
# arcStart = time.clock()
import arcpy
from arcpy import env
env.overwriteOutput = True
# arcImportTime = time.clock() - arcStart
# print "Arc Import Time: {}".format(arcImportTime)
# startTime = time.clock()




# Inputs
faultShp = r'D:\Workspace\projects\RussianRiver\Data\geology\faults\RR_mod_faults_combine.shp'
parnamField = 'parnam'
parvalField = 'Paramvalue'
hydCharField = 'Paramvalue'
fltTopLyrField = 'toplayer'
fltBotLyrField = 'toplayer'
mgShp = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
rowField = 'HRU_ROW'
colField = 'HRU_COL'
# iboundFields = sys.argv[].split(';')
numOfSP = 3
otHFB_shp = r"D:\Workspace\projects\RussianRiver\Data\geology\faults\hru_faults.shp"
hfb_mdflow = r"D:\Workspace\projects\RussianRiver\Data\geology\faults\rr.hfb"
otHFB_file = open(hfb_mdflow, 'w')

otFolder = os.path.dirname(otHFB_shp)
otHFB_shp_base = os.path.basename(otHFB_shp)

# maxLyr = len(iboundFields)



curFields = [rowField, colField]
# get information from the model grid
rows = arcpy.da.SearchCursor(mgShp, curFields)
rowMax = ''
rowMin = ''
colMax = ''
colMin = ''

# iboundDic = {}
# for i in range(1, len(iboundFields) + 1):
#     iboundDic[i] = {}
for idx, row in enumerate(rows):
    rowVal = int(row[0])
    colVal = int(row[1])
    # for i, ibField in enumerate(iboundFields):
    #     curIdx = curFields.index(ibField)
    #     iboundDic[i + 1][(rowVal, colVal)] = int(row[curIdx])
    if idx == 0:
        rowMax, rowMin = rowVal, rowVal
        colMax, colMin = colVal, colVal
        # angle = row[2]
    else:
        rowMax, rowMin = getMax(rowMax, rowVal), getMin(rowMin, rowVal)
        colMax, colMin = getMax(colMax, colVal), getMin(colMin, colVal)
del row
del rows

# get the number of rows and columns
numOfRows = (rowMax - rowMin) + 1
numOfCols = (colMax - colMin) + 1


# print "check 0", time.clock() - startTime


# Calculate polygon main angle #
whereClause = '"{0}" = 1 AND "{1}" = 1 OR "{0}" = {2} AND "{1}" = 1'.format(rowField, colField, numOfRows)
rows = arcpy.da.SearchCursor(mgShp, [rowField, colField, "SHAPE@TRUECENTROID", "SHAPE@AREA"], whereClause)
centroidDic = {}
for idx, row in enumerate(rows):
    if idx == 0:
        cellArea = row[3]
    centroidDic[((int(row[0]) * 1000) + int(row[1]))] = row[2]
del row
del rows

fromPt = centroidDic[max(centroidDic.keys())]
toPt = centroidDic[min(centroidDic.keys())]
mainAngle, perpAngle, invMainAngle, invPerpAngle = getAngles(fromPt, toPt)


# print "Polygon main angle is {}".format(mainAngle)

# print mainAngle, perpAngle, invMainAngle, invPerpAngle

# print "check 1", time.clock() - startTime




arcpy.MakeFeatureLayer_management(mgShp, 'mgShp')
# select the model grid cells that the fault lines intersect
arcpy.SelectLayerByLocation_management('mgShp', "INTERSECT", faultShp, selection_type="NEW_SELECTION")
# output intersected polygons
# arcpy.CopyFeatures_management('mgShp', r"in_memory\\intersect")
# create centroid shapefile of intersected cells
centroids = arcpy.FeatureToPoint_management('mgShp', os.path.join(otFolder, 'centroids.shp'))
# centroids = arcpy.FeatureToPoint_management('mgShp', r'.\centroids.shp')
# arcpy.CopyFeatures_management(centroids, ".\intersect.shp")

# print "check 2", time.clock() - startTime

# ------------- MAKE TRIGGERS ______________________#

# cell wall length
# print cellArea
cellLen = math.sqrt(cellArea)
trigLen = cellLen/2.0
diagLen = math.sqrt(2) * trigLen
# print trigLen

# dictionary to store trigger lines
triggerDic = {}
centroidDic = {}
# # search cursor on centroids
rows = arcpy.da.SearchCursor(centroids, [rowField, colField, "SHAPE@XY"])
for row in rows:
    rowcol = (row[0], row[1])
    centroidXY = row[2]
    centroidDic[rowcol] = centroidXY
    triggerDic[rowcol] = {}
    point = getPoint(mainAngle, trigLen, centroidXY)
    array = arcpy.Array([arcpy.Point(centroidXY[0], centroidXY[1]), arcpy.Point(point[0], point[1])])
    polyline = arcpy.Polyline(array)
    # print point
    triggerDic[rowcol][1] = polyline
    point = getPoint(perpAngle, trigLen, centroidXY)
    array = arcpy.Array([arcpy.Point(centroidXY[0], centroidXY[1]), arcpy.Point(point[0], point[1])])
    polyline = arcpy.Polyline(array)
    # print point
    triggerDic[rowcol][2] = polyline

    point = getPoint(invMainAngle, trigLen, centroidXY)
    array = arcpy.Array([arcpy.Point(centroidXY[0], centroidXY[1]), arcpy.Point(point[0], point[1])])
    polyline = arcpy.Polyline(array)
    triggerDic[rowcol][3] = polyline

    point = getPoint(invPerpAngle, trigLen, centroidXY)
    array = arcpy.Array([arcpy.Point(centroidXY[0], centroidXY[1]), arcpy.Point(point[0], point[1])])
    polyline = arcpy.Polyline(array)
    triggerDic[rowcol][4] = polyline

# print "check 3", time.clock() - startTime

### --- Build trigger shapefile --- ####

# create trigger polyline feature class
triggersShp = arcpy.CreateFeatureclass_management('in_memory', 'triggers', "POLYLINE", spatial_reference=mgShp)
# arcpy.AddField_management(triggersShp, "CELLNUM", "LONG")
arcpy.AddField_management(triggersShp, "ROWVAL", "LONG")
arcpy.AddField_management(triggersShp, "COLVAL", "LONG")
arcpy.AddField_management(triggersShp, "SEGID", "LONG")


# print "check 4", time.clock() - startTime

insert = arcpy.da.InsertCursor(triggersShp, ["ROWVAL", "COLVAL", 'SEGID', "SHAPE@"])
for (rowVal, colVal), triggers in sorted(triggerDic.iteritems()):
    for segID, triggerLine in sorted(triggers.iteritems()):
        insert.insertRow([rowVal, colVal, segID, triggerLine])
del insert

# print "check 5", time.clock() - startTime

### ---- BUILD OUT HFB SEGS ---- ###
intersect = arcpy.Intersect_analysis([faultShp, triggersShp], r'in_memory\\falt_trigger_intersect', output_type="POINT")

otAngDic = {1: perpAngle, 2: invMainAngle, 3: invPerpAngle, 4: mainAngle}
diagAngDic = {}
for i in range(1, 5):
    if i == 1:
        diagAng = mainAngle - 45
    else:
        diagAng += 90
    diagAngDic[i] = diagAng

# print "check 6", time.clock() - startTime

# dictionary for storing parmater values by parnam
parDic = {}
# dictionary for storing out hfb lines
hfbLinesDic = {}
hfbLyrsDic = {}
rows = arcpy.da.SearchCursor(intersect, ["ROWVAL", "COLVAL", "SEGID", parnamField, parvalField, fltTopLyrField, fltBotLyrField, hydCharField])
for row in rows:
    rowVal = row[0]
    colVal = row[1]
    segID = row[2]
    parnam = row[3]
    # arcpy.AddMessage(parnam)
    parval = row[4]
    fltTopLyr = row[5]
    fltBotLyr = row[6]
    hydChar = row[7]

    if parnam not in parDic:
        parDic[parnam] = parval, hydChar
        hfbLinesDic[parnam] = {}
        hfbLyrsDic[parnam] = {}

    mkHFB = True
    # arcpy.AddMessage("top lyr {}, bot Lyr {}".format(fltTopLyr, fltBotLyr))
    for lyr in range(fltTopLyr, fltBotLyr + 1):
        # lyrIbound = iboundDic[lyr]
        # if lyrIbound[(rowVal, colVal)] != 0:
        connection = buildConn(rowVal, colVal, segID)
        if checkBounds(connection.otRow, connection.otCol, numOfRows, numOfCols):
            # if lyrIbound[(connection.otRow, connection.otCol)] != 0:
            connection.build()
            if mkHFB:
                p1 = getPoint(diagAngDic[segID], diagLen, centroidDic[(rowVal, colVal)])
                p2 = getPoint(otAngDic[segID], cellLen, p1)
                array = arcpy.Array([arcpy.Point(p1[0], p1[1]), arcpy.Point(p2[0], p2[1])])
                polyline = arcpy.Polyline(array)
                hfbLinesDic[parnam][connection.conn] = polyline
                hfbLyrsDic[parnam][connection.conn] = str(lyr)
                mkHFB = False
            else:
                hfbLyrsDic[parnam][connection.conn] += ',{}'.format(lyr)


# total paramters
parCount = len(parDic.keys())

# arcpy.AddMessage(hfbLyrsDic['ELMO_UWB'])

# print "check A", time.clock() - startTime

# total output
totalVals = 0
for parnam, lyrDic in sorted(hfbLyrsDic.iteritems()):
    for conn, lyrsStr in sorted(lyrDic.iteritems()):
        lyrCount = len(lyrsStr.split(','))
        totalVals += lyrCount


otHFB_file.write('{} {} 0\n'.format(parCount, totalVals))

# print "check 7", time.clock() - startTime


hfbShp = arcpy.CreateFeatureclass_management(otFolder, otHFB_shp_base, "POLYLINE", spatial_reference=mgShp)
arcpy.AddField_management(hfbShp, "ROWVAL_1", "LONG")
arcpy.AddField_management(hfbShp, "COLVAL_1", "LONG")
arcpy.AddField_management(hfbShp, "ROWVAL_2", "LONG")
arcpy.AddField_management(hfbShp, "COLVAL_2", "LONG")
arcpy.AddField_management(hfbShp, "PARNAM", "TEXT")
arcpy.AddField_management(hfbShp, "PARVAL", "TEXT")
arcpy.AddField_management(hfbShp, "HYDCHAR", "TEXT")
arcpy.AddField_management(hfbShp, "LYRS", "TEXT")



otDic = {}
insert = arcpy.da.InsertCursor(hfbShp, ["ROWVAL_1", "COLVAL_1", "ROWVAL_2", "COLVAL_2", "PARNAM", "PARVAL", "HYDCHAR", "LYRS", "SHAPE@"])
for parnam, (parval, hydChar) in sorted(parDic.iteritems()):
    hfbLines = hfbLinesDic[parnam]
    hfbLyrs = hfbLyrsDic[parnam]
    # parValCount = 0
    # hfbStr = ''
    otDic[parnam] = []
    for otConn, hfb in sorted(hfbLines.iteritems()):
        rowVal1, colVal1, rowVal2, colVal2 = otConn
        lyrs = hfbLyrs[otConn]
        insert.insertRow([rowVal1, colVal1, rowVal2, colVal2, parnam, parval, hydChar, lyrs, hfb])
        for lyr in lyrs.split(','):
            otDic[parnam].append((lyr, str(rowVal1), str(colVal1), str(rowVal2), str(colVal2)))
            # parValCount += 1
            # hfbStr += '{} {} {} {} {} 1\n'.format(lyr, rowVal1, colVal1, rowVal2, colVal2)
    # otHFB_file.write('{} HFB {} {}\n{}'.format(parnam, parval, parValCount, hfbStr))
del insert


print otDic

for parnam, hfbs in sorted(otDic.iteritems()):
    parValCount = 0
    hfbStr = ''
    parval = parDic[parnam][0]
    hydChar = parDic[parnam][1]
    for hfb in sorted(hfbs):
        parValCount += 1
        hfbStr += "{} {}\n".format(' '.join(hfb), hydChar)
        # hfbStr += '{} {} {} {} {} 1\n'.format(lyr, rowVal1, colVal1, rowVal2, colVal2)
    otHFB_file.write('{} HFB {} {}\n{}'.format(parnam, parval, parValCount, hfbStr))





for sp in range(1, numOfSP + 1):
    otHFB_file.write('{}\n{}\n'.format(len(parDic.keys()), '\n'.join(sorted(parDic.keys()))))
otHFB_file.close()


arcpy.Delete_management(centroids)
pass
# END ARC #
