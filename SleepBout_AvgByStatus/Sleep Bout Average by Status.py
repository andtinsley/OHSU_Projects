import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

path = os.getcwd()

# read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.txt"))


#get light time inputs 
if __name__ == "__main__":
    lightsOn = input("Input lights on time (format x:xx AM/PM): ")
    lightsOff = input("Input lights off time (format x:xx AM/PM): ")

#lightsOn = '6:00 AM'
#lightsOff = '6:00 PM'
def convertTime(getTime):
    stripTime = datetime.strptime(getTime, '%I:%M %p').time()
    return stripTime
lightsOn = convertTime(lightsOn)
lightsOff = convertTime(lightsOff)

#setup loop for calculating average bouts per file and group
d_list = []
for file in filenames:

    getSubject = file.split('\\')[-1]
    getSubject = getSubject.split('.')[0]
    
    d=pd.read_csv(file, skiprows= 17, delimiter='\t',  escapechar='\\', usecols=['Time', 'Stage'])
    d=d.iloc[1: , :]
    d.Time = pd.to_datetime(d.Time)
    d['File'] = getSubject

    
    #strip time
    d['DateTime'] = d['Time']
    d['Time'] = d['Time'].dt.time

    #strip date
    d['Date']=d.DateTime.dt.date

    d['LightsOn'] = lightsOn
    d['LightsOff'] = lightsOff

    d['IsLightsOn'] = np.where((d['Time']>=d['LightsOn']) & (d['Time']<d['LightsOff']),  1, 0)

    #time difference between time points is always four seconds
    d['StageTime'] = 4

    d['NextStage']=(d['Stage'].shift(-1))
    d['IsTransition'] = np.where(d['Stage'] == d['NextStage'], 0, 1)
    
    #calculate average bout length in seconds per lights on and stage
    #get bout length
    def getBoutSum(dataset):
        dataset['StageID'] = dataset['IsTransition'].cumsum()
        dataset = dataset.groupby(["File","Date", "IsLightsOn",'StageID', "Stage"])['StageTime'].sum().reset_index()
        dataset['StageID'] = dataset['StageID'].astype(int)
        return dataset
    
    d = getBoutSum(d)

    #average bout lengths per file, light and stage

    def getBoutAvg(dataset):
        dataset = dataset.groupby(['File', 'IsLightsOn','Stage'])['StageTime'].mean().reset_index()
        dataset = dataset.rename(columns={"StageTime": "Average Bout Length (seconds)"})
        return dataset
    
    d = getBoutAvg(d)
    d_list.append(d)
DF_Stages = pd.concat(d_list, axis=0, ignore_index=True) 
DF_Stages.sort_values(['File', 'IsLightsOn', 'Stage'])
DF_Stages['Average Bout Length (seconds)']=DF_Stages['Average Bout Length (seconds)'].round(3)
DF_Stages.to_csv('Average Bout Length.csv', index=False)
print(f"File '{'Average Bout Length.csv'}' created successfully.")