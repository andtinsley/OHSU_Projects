import pandas as pd
import os
import glob
import string as str


# read all the files with extension .csv
path = os.getcwd()

# read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.csv"))

d_list = []

for file in filenames:
   # reading csv files
   d = pd.read_csv(file, index_col=None, header=0)

   #get sample name from file
   file_name=file.split('_')[-2]
   d["Sample"] = file_name

   # drop all but year from column names
   #d.columns.str.replace('(\-\w+.*?)',"")
   renameColumns = d.columns.str.replace(r'\S*\-\S*','')
   d.columns = renameColumns

   mergeDuplicates = d.sum(axis=1, level=0)
   mergeDuplicates = mergeDuplicates.reindex(sorted(mergeDuplicates.columns), axis=1)


   d_list.append(mergeDuplicates)


final_output = pd.concat(d_list, axis=0, ignore_index=True) 
#re order columns 0->23
final_output = final_output.reindex(sorted(final_output.columns), axis=1)
#set Sample and Transition as index
final_output = final_output.set_index(['Sample', 'Transition'])
final_output.to_csv("SleepOutputConcatenate.csv", index=True)