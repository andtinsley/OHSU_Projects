import pandas as pd
import numpy as np
import os
import glob


pd.options.mode.chained_assignment = None
path = os.getcwd()
    # read all the files with extension .csv
filenames = glob.glob(os.path.join(path, "*.csv"))

d_list = []
for file in filenames:
    d=pd.read_csv(file)
    d_list.append(d)

final_output = pd.concat(d_list, axis=0, ignore_index=True) 
final_output.to_csv('Output.csv', index=False)