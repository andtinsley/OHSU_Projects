

import pandas as pd
import os
import glob
import sys
import numpy as np
import re

## For each text file in folder:
## 1) Create an excel extract
## 2) compare all matrix values and return:
##    a) occurrences of values (number of times a correlation was present)
##    b) Z-Score from correlation coefficient
##    c) Updated Correlation coefficient from an averaged z-score
# getting csv files from the folder MyProject

#os.chdir(os.path.dirname(__file__))
#path = os.getcwd()



# determine if application is a script file or frozen exe
path = os.getcwd()

# read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.txt"))
newpath = path+'/Extract'
if not os.path.exists(newpath):
   os.makedirs(newpath)


d_list = []
z_list = []
# for loop to iterate all txt files
# save copy for edit
for file in filenames:
   # reading csv files
   d = pd.read_csv(file, sep=';')
   
   
   #drop duplicated columns: columns with period present
   d.drop([col for col in d.columns if '.' in col],axis=1, inplace=True)
   #drop duplicated rows
   d = d.drop_duplicates(subset=['Matrix'])
   file_name = file.rsplit(' ', 1)[1]
   file_name = file_name.rsplit('.', 1)[0]   
   #d.to_excel(newpath+"\\"+file_name + ".xlsx", index = False)  
   #z-score
   d_indexed = d.set_index('Matrix')
   #drop duplicated columns by identifying where columns have a period
   
   
   ##(1/2)log( (1+r)/(1-r))
   numeric_cols = [col for col in d_indexed if d_indexed[col].dtype.kind != 'O']
   d_z_score = (1+d_indexed[numeric_cols]) / (1-d_indexed[numeric_cols])
   d_z_score = np.log10(d_z_score) / 2
   d_z_score.reset_index(drop=False, inplace=True)
   #Export
   # create a excel writer object
   d.to_csv(newpath+"\\"+file_name +".csv", index=False)
   d_z_score.to_csv(newpath+"\\"+"Z Scores_"+file_name+ ".csv", index=False)

   d_list.append(d)
   z_list.append(d_z_score)

df_final=pd.concat(d_list)
z_score=pd.concat(z_list)

#average Z_score
average_z_score = z_score.groupby('Matrix').mean()
#count of occurences
n_matrix = df_final.groupby('Matrix').count()

#transpose data for analysis
make_long=average_z_score.stack().reset_index()
make_long['corr_features'] = make_long['Matrix'] +' x ' + make_long['level_1']
make_long = make_long[['corr_features', 0]]
make_long = make_long.set_index('corr_features').T.reset_index()
make_long = make_long.iloc[: , 1:]


#export 
#file name
updated_file_name = file_name.split('_', 1)[-1]
updated_file_name = updated_file_name.split("_")[0]
  
nextpath = path+'/Calculated'
if not os.path.exists(nextpath):
   os.makedirs(nextpath)
# create a excel writer object


#with pd.ExcelWriter(nextpath+"\\"+updated_file_name + ".xlsx") as writer:
#  average_z_score.to_excel(writer, sheet_name="Average Z", index=True)
  # n_matrix.to_excel(writer, sheet_name="Samples", index=True)
   #make_long.to_excel(writer, sheet_name="Avg Z Trans", index=False)

average_z_score.to_csv(nextpath+"\\"+ "Average_Z_Score_"  + updated_file_name +".csv", index=False)
n_matrix.to_csv(nextpath+"\\"+ "Samples_"  + updated_file_name +".csv", index=False)
make_long.to_csv(nextpath+"\\"+ "Long_"  + updated_file_name +".csv", index=False)