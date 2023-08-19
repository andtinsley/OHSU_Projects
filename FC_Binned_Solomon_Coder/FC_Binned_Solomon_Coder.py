import pandas as pd
import os
import glob
import numpy as np


pd.options.mode.chained_assignment = None
path = os.getcwd()
    # read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.csv"))


if __name__ == "__main__":
    getBucket = int(input("Enter the size of bins: "))


#get all subject files
subjectFiles = []
for subjectFile in filenames:
    getFilename = subjectFile.rsplit('\\')[-1]
    getFilename = getFilename.split(".")[0]
    getFilename = getFilename.split("-")[0]
    subjectFiles.append(getFilename)
subjectFiles = np.unique(subjectFiles)



subjectPD = []
for eachSubject in subjectFiles:
    filesNeeded = [v for v in filenames if eachSubject in v]
    
    d_list = []
    fields = ['Time', 'Movement','Supplemental','Cues']
    
    for file in filesNeeded:
        fileNumber = file.rsplit('_')[-1]
        fileNumber = fileNumber.rsplit('.')[0]

        #get subject name
        subjectFile = file.rsplit('\\')[-1]
        Subject = subjectFile.rsplit('_')[0]
        # if numbered then file is a subsequent sequence else first sequence
    
        if '-' in fileNumber:
            fileNumber = fileNumber.split('-')[1]
        else:
            fileNumber = 1
        #only include data abover first blank row (delete summary data at bottom of set)
        d = pd.read_csv(file, header=0, usecols=fields, skip_blank_lines=False)
        blank_df = d.loc[d.isnull().all(1)]
        if len(blank_df) > 0:
            first_blank_index = blank_df.index[0]
            d = d[:first_blank_index]
        
        d['Sequence'] = int(fileNumber)
        d['Subject'] = Subject
        d['Time'] = d['Time'].astype('float')

        d_list.append(d)
    d=pd.concat(d_list, axis=0, ignore_index=True)
    # Order by Sequence and time and replace time column to start from zero and increase by .2 incr
    d=d.sort_values(by=['Sequence', 'Time'], ascending=[True, True]).reset_index(drop=True)

    d['CumCount'] = .2
    d['Time'] = d['CumCount'].cumsum()-.2

    #read csv
    
    d['BucketOrder'] = d.loc[:,'Time'] / getBucket+1
    d['BucketOrder'] = np.floor(d.BucketOrder).astype('int')
    #only include timepoints with movement
    d = d.dropna(subset=['Movement'])
    d["TotalTime"] = d.loc[:,'Time'].diff().round(1)
    #remove starting times as not separated by .2
    removeGapTime = d.loc[:,"TotalTime"] == 0.2
    d = d[removeGapTime]

    #insert a zero bucket if there is not a bucket
    
    hasBuckets = d['BucketOrder'].unique()
    maxBucket = d['BucketOrder'].max()
    missingBucket = np.arange(1, maxBucket+1)
    missingBucket = np.setxor1d(hasBuckets, missingBucket)
    missingBucket = np.concatenate((hasBuckets, missingBucket))
    missingBucket=pd.DataFrame(missingBucket, columns=['Bucket_Updated']).sort_values(['Bucket_Updated'])
    #cross join with all movements
    missingBucket['key']=1
    AllMovements = pd.DataFrame(d['Movement'].unique(), columns = ['AllMovements'])
    AllMovements['key']=1
    missingBucket=pd.merge(AllMovements, missingBucket, on='key').drop('key', axis=1)
    d=d.merge(missingBucket, how='outer', left_on=['BucketOrder', 'Movement'], right_on=['Bucket_Updated', 'AllMovements']).fillna(0).sort_values(['Bucket_Updated', 'Time'])

    d['Bucket_Updated'] = d['Bucket_Updated'].astype('int')
    d['Bucket'] = ((d.Bucket_Updated-1)*getBucket).astype(str)+"-"+(d.Bucket_Updated*getBucket).astype(str)
    
    # collect only columns of interest and group sums by buckets
    d = d.loc[:,['Bucket_Updated', 'Bucket', 'AllMovements', 'TotalTime']]
    d = d.groupby(['Bucket_Updated', 'Bucket','AllMovements']).sum()
    #drop bucket order
    d = d.reset_index()
    d = d.drop('Bucket_Updated', axis=1)

    #round to nearest tens
    d['TotalTime'] = d['TotalTime'].round(2)

    #add subject
    d['Subject'] = Subject

    #make data wide
    makeWide = d.pivot(index=['Subject', 'AllMovements'], columns='Bucket', values='TotalTime')
    cols=d['Bucket'].unique()
    d = makeWide[cols]

    #export file
    outputName = filesNeeded[-1].split('\\')[-1]
    outputName = outputName.split('.')[0]
    outputName = outputName.split('-')[0]
    outputName = outputName +"_BucketSize_" +str(getBucket)
    d.to_csv(outputName+'.csv', index=True)
    print(f"File '{outputName}' created successfully.")