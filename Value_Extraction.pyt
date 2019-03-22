# Value_Extraction.pyt
# Version: I
# Fall 2018
# Author: Grant Haynes
# 
# Arc Version:
# This tool was developed and tested with Arcmap 10.6
#
# IDE:
# This tool was developed in Visual Studio Code
#
# Purpose:
# This tool will extract values of rasters in a folder and send those
# values to a data file for plotting. This tool will be published as a 
# asynchronus geoprocessing service
#
#-----------------------------------------------------------------------------

# Start script
#-----------------------------------------------------------------------------
import arcpy
import os

# Tool initialization
#-----------------------------------------------------------------------------
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Value_Extraction_Tool"
        self.alias = "Value Extraction Tool"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Value Extraction Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        DataSource = arcpy.Parameter(
		    displayName="DataSource",
		    name="DataSource",
		    datatype="DEWorkspace",
		    parameterType="Required",
		    direction="Input")

        InputX = arcpy.Parameter(
		    displayName="InputX",
		    name="InputX",
		    datatype="GPString",
		    parameterType="Required",
		    direction="Input")

        InputY = arcpy.Parameter(
            displayName="InputY",
		    name="InputY",
		    datatype="GPString",
		    parameterType="Required",
		    direction="Input")

        Output = arcpy.Parameter(
            displayName="Output",
		    name="Output",
		    datatype="DEShapefile",
		    parameterType="Required",
		    direction="Output")

        params = [DataSource, InputX, InputY, Output]
        return params

    def isLicensed(self):
        # Set whether tool is licensed to execute.
        return True

    def updateParameters(self, parameters):
        # Modify the values and properties of parameters before internal
        # validation is performed.  This method is called whenever a parameter
        # has been changed.
        return

    def updateMessages(self, parameters):
        #Modify the messages created by internal validation for each tool
        #parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        #The source code of the tool.

        # User input arguments
        DataSource = parameters[0].valueAsText
        InputX = parameters[1].valueAsText
        InputY = parameters[2].valueAsText
        Output= parameters[3].valueAsText

        # Create a point layer
        pt = arcpy.Point()
        pt.X = InputX
        pt.Y = InputY
        ptGeom = arcpy.PointGeometry(arcpy.Point(InputX, InputY))
        arcpy.CopyFeatures_management(ptGeom, Output)

        #assign coordinate system
        sr = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(Output, sr)
        
        # Get rasters and extract data at an X and Y        
        index = 0
        for (path, dirs, files) in os.walk(DataSource):
            for ThisFile in files:
                fName,fExt = os.path.splitext(ThisFile)
                if fExt.upper() == ".IMG" or fExt.upper() == ".TIF":
                    RasterPath = path + "\\" + ThisFile
                    aquisition_date = arcpy.GetRasterProperties_management(in_raster=RasterPath, property_type='ACQUISITIONDATE')
                    data = arcpy.GetCellValue_management(RasterPath, InputX + " " + InputY, "")

                    # add data into fields
                    if str(aquisition_date).upper() == "UNKNOWN":
                        # create record field and populate
                        arcpy.AddField_management(Output, "F" + str(index), "Short", "", "", "", "", "", "", "")
                        arcpy.CalculateField_management(Output, "F" + str(index) ,index,"PYTHON", "")

                        arcpy.AddField_management(Output, "V"+ str(index), "Double", "", "", "", "", "", "", "")
                        arcpy.CalculateField_management(Output,"V"+ str(index), data,"PYTHON", "")

                    else:
                        arcpy.AddField_management(Output, "Dt"+ str(index), "Date", "", "", "", "", "", "", "")
                        arcpy.CalculateField_management(Output, "Dt"+ str(index), aquisition_date, "PYTHON", "")

                        arcpy.AddField_management(Output, "V"+ str(index), "Double", "", "", "", "", "", "", "")
                        arcpy.CalculateField_management(Output,"V"+ str(index), data,"PYTHON", "")

                    index += 1
        return