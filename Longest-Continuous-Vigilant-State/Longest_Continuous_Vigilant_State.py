#!/usr/bin/env python
# coding: utf-8

# In[141]:


import pandas as pd
import os
from pathlib import Path
import glob

#empty container for appending data passed in for loop
FinalDF = []

#collect text file
# Use the for loop to iterate through the list you just created, and open the files
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.txt"))
# loop over the list of csv files
for f in csv_files:
    d = pd.read_csv(f, skiprows=17, sep='\t')
    d['Time'] = pd.to_datetime(d['Time'], format='%m/%d/%Y %H:%M:%S')
#remove first row
    d = d[1:]
# find if row below is different stage then current 
    d= d[['Time', 'Stage']]
    d['Stage']=d['Stage'].astype('category')
    d['nStage']=d['Stage'].shift(-1)
    i=d.nStage
    d['Inc']=i.ne(i.shift()).cumsum()
    d['Inc']=d['Inc'].shift(+1).bfill()
    d=d.drop(['nStage'], 1)
    #time in stage
    d['TimeInStage'] = 4
    d=d.groupby(['Stage', 'Inc'])['TimeInStage'].agg('sum').reset_index()
    d=d.groupby(['Stage'])['TimeInStage'].agg('max').reset_index()
    d=d.set_index('Stage')
    
#add filename to column file    
    fileString = f.split('\\')[-1]
    d['File'] = fileString
    d.reset_index(inplace=True)
#pivot    
    d=d.pivot(index='File', columns='Stage', values='TimeInStage')
    
    FinalDF.append(d)

#concat to pandas DF and Export as csv
FinalDF=pd.concat(FinalDF)
FinalDF.to_csv('LongestVigilantState.csv')

