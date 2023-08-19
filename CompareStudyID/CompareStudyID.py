import pandas as pd
import glob
import os
import numpy as np

data = pd.DataFrame()
data['StudyId']=""
globbed_files = glob.glob("*.csv")
for csv in globbed_files:
    frame = pd.read_csv(csv, header=None)
    frame.columns=['StudyId']
    frame['filename'] = os.path.basename(csv)
    frame['StudyId'] = frame['StudyId'].str.rsplit('.', n=1).str[0].str.split('.').str[-1]
    frame['filename'] = frame['filename'].str.rsplit('.', n=1).str[0].str.split('.').str[-1]
    frame['StudyId'] = frame['StudyId'].str.rsplit('\\', 1).str[1]
    frame = frame.drop_duplicates(subset=['StudyId'])
    data = pd.merge(frame, data, on='StudyId', how='outer')



    
dropFirstColumn = data.iloc[: , 1:]
StudyIdColumn = data.iloc[: , :1]

listOfColumnNames = []
for col in dropFirstColumn:
    d = dropFirstColumn[col].unique()
    d = [x for x in d if str(x) != 'nan']
    listOfColumnNames.append(d[0])
dropFirstColumn.columns = listOfColumnNames
#replace values with 1 or blanks
dropFirstColumn = dropFirstColumn.notna()
dropFirstColumn = dropFirstColumn.astype('int').astype('string').replace(['0', '0.0'], '')
dropFirstColumn['StudyId'] = StudyIdColumn
finalSet = dropFirstColumn.set_index('StudyId')

finalSet.to_csv("Compare Study Results.csv", index=True)


