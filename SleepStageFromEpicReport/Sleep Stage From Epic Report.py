import pandas as pd
import glob
import os

path = os.getcwd()
# read all the files with extension xlsx
filenames = glob.glob(os.path.join(path, "*_EpochReport.xlsx"))

# collect first two columns. File name to match subject ID from file

for file in filenames:
   # reading csv files
   d = pd.read_excel(file)
   d=d.iloc[:,0:2]
   file_name = file
   file_name = file_name.rsplit('\\', 1)[-1]
   file_name = file_name.split('.')[0]
   file_name = file_name.split('_')[0]
   file_name = file_name+'_SleepStageReport'
   d.to_excel(file_name + '.xlsx', index=False)