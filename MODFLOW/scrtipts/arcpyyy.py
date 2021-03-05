import os, sys
d = r"C:\ArcGIS\Pro\bin"; os.environ["PATH"] = r"{};{}".format(d, os.environ["PATH"])
d = r"C:\ArcGIS\Pro\bin"; sys.path.insert(-1,d)
d = r"C:\ArcGIS\Pro\Resources\ArcPy"; sys.path.insert(-1,d)
d = r"C:\ArcGIS\Pro\Resources\ArcToolbox\Scripts"; sys.path.insert(-1, d)
e = "FOR_DISABLE_CONSOLE_CTRL_HANDLER"; os.environ[e] = '1' if (not e in os.environ) else ""
d = r"C:\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Lib\site-packages"; sys.path.insert(-1, d)
import geopandas
import arcpy
xx = 1
