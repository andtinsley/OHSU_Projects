import pandas as pd
import numpy as np
import os
import glob


path = os.getcwd()

# read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.txt"))


SubjectContainer = []
for file in filenames:
    
    Subject = file.split('_')[0]
    Subject = Subject.split('\\')[-1]
    d=pd.read_csv(file, skiprows= 18, header=None, delimiter='\t',  escapechar='\\')

    #identify break of dataframe by Total verbiage
    getBreak = d[d[0]=='Total']
    getBreak = getBreak[[0]].assign(df_Break=range(len(getBreak)))
    d = pd.merge(d, getBreak, how='left', left_index=True, right_index=True)
    d['df_Break'] = d['df_Break'].bfill()
    d['df_Break'] = d['df_Break'].astype(int)

    #for each dataframe make data long
    grouped = d.groupby('df_Break')
    
    StageContainer = []
    for name, group in grouped:
        
        #remove not needed header details
        removeHeaderData = group["0_x"].str.contains('Time Division')==False
        group = group[removeHeaderData]


        #drop break column
        Session = group.drop('df_Break', axis=1)

        #Session.to_csv(Subject +"test.csv")
        Session.reset_index(drop=True, inplace=True)

        #get stage data
        getStage = Session[2][0]
        Session = Session.drop(Session.index[[0,1]])

        #drop junk column
        Session = Session.drop('0_y', axis=1)

        ColumnHeader = Session['0_x']
        Session = Session.drop('0_x', axis=1)

        #convert to numeric
        Session = Session.astype(np.float64)

        Session = Session.sum(numeric_only=True,axis=1)

        Session = pd.merge(ColumnHeader.to_frame(), Session.to_frame(), how='inner', left_index=True, right_index=True)
        
        Session = Session.transpose()
        Session.columns = Session.iloc[0]
        Session = Session.iloc[1:].reset_index(drop=True)



        Session.to_csv("test.csv")

        print(Session)
        Session['Stage'] = getStage

        Session['Subject'] = Subject
        StageContainer.append(Session)

    StagedData = pd.concat(StageContainer)

    SubjectContainer.append(StagedData)

FinalSet = pd.concat(SubjectContainer)


FinalSet = FinalSet.set_index(["Subject", "Stage"])

FinalSet.to_csv("Concatenated Data.csv", index=True)