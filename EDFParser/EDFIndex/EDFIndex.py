import pandas as pd
import mne
import os
import datetime
import glob
import pickle

#output file name
getScriptWD = os.path.dirname(os.path.realpath(__file__))
EDFIndexFile = getScriptWD + "\\EDFIndex.pkl"


#search filepath location
fileLocation = input("Enter File Path of EDF Files ")
filenames = glob.glob(os.path.join(fileLocation, "*.edf"))

## definitions
#get subject from file name
def getFileName(file):
    file_name = file.rsplit('\\', 1)[-1]
    file_name = file_name.split('.')[0]
    return file_name

#get measurementdate
def getMeasurementDate(file):
    getDate = metaData = mne.io.read_raw_edf(file)
    getDate = metaData.info["meas_date"]
    getDate = pd.to_datetime(getDate, format='%Y,%m,%d,%H,%M,%S')
    return getDate

##If pickle is found
##upload pickle and find maximum date for update
try:
    getExistingRecords = pd.read_pickle(EDFIndexFile)
    print("Searching for new files")
    
    FileName = []

    for file in filenames:
    
        #get subject from file name
        file_name = getFileName(file)
        FileName.append(file_name)

    ExistingRecordsList = getExistingRecords['FileName'].values.tolist()

        #identify new records
    getNewFiles = list(set(FileName) - set(ExistingRecordsList))

    MeasurementDate = []
    FileName = []

    for file in getNewFiles:
            #add file type extension
        fileName = "/"+file+".edf"
        fileName = fileLocation+fileName

            #get measurementdate

        getDate = getMeasurementDate(fileName)
        MeasurementDate.append(getDate)
            
    NewFiles = pd.DataFrame({"MeasurementDate": MeasurementDate, "FileName": getNewFiles})

        #collect year from measureent and set as index
    NewFiles["MeasurementYear"] = NewFiles["MeasurementDate"].dt.year
    NewFiles = NewFiles.set_index("MeasurementYear")

    print("Updating storage file in progress")

    df = pd.concat([getExistingRecords, NewFiles], axis=0)
    df.to_pickle(EDFIndexFile)
    print("Storage file update completed")

except FileNotFoundError:
    print("Storage file not found. Creating new reference file.")
    
    MeasurementDate = []
    FileName = []

    for file in filenames:
        
        #get subject from file name
        file_name = getFileName(file)
        FileName.append(file_name)
        
        #get measurementdate
        getDate = getMeasurementDate(file)
        MeasurementDate.append(getDate)

    df = pd.DataFrame({"MeasurementDate": MeasurementDate, "FileName": FileName})

    #collect year from measureent and set as index
    df["MeasurementYear"] = df["MeasurementDate"].dt.year
    ##df["MeasurementYear"] = df["MeasurementDate"].astype(str)
    df = df.set_index("MeasurementYear")

    print("Updating storage file in progress")

    df.to_pickle(EDFIndexFile)
    print("Storage file update completed")

