import pandas as pd
import os

getYearNeeded = input("Enter measurement year for record search: ")

#output file name
getScriptWD = os.path.dirname(os.path.realpath(__file__))
EDFIndexFile = getScriptWD + "\\EDFIndex.pkl"

getAllRecords = pd.read_pickle(EDFIndexFile)

filterDate = getAllRecords.index == int(getYearNeeded)
recordsRequested = getAllRecords[filterDate]


recordsRequested.to_csv(getScriptWD+ "/Records Requested for Year "+getYearNeeded+".csv")