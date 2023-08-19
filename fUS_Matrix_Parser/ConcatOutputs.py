import pandas as pd
import os
import glob
import sys
import numpy as np
import re

path = os.getcwd()

# read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.csv"))

d_list = []

for file in filenames:
   # reading csv files
   d = pd.read_csv(file, index_col=None, header=0)

   file_name = file
   file_name = file_name.split('.')[0]
   file_name=file_name.split('_')[1]
   d["Sample"] = file_name
   d_list.append(d)

final_output = pd.concat(d_list, axis=0, ignore_index=True)
final_output.to_csv("ConcatResults.csv", index=False)
    