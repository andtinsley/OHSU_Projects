import pandas as pd
import tkinter as tk
import os
import numpy as np
from pathlib import Path
import glob

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.mainap = tk.Button(self,
                                width=20,
                                height=5,
                                bg="blue",
                                fg="white")
        self.mainap["text"] = "Duration\n of\n Sleep Stage"
        self.mainap["command"] = self.mainapp
        self.mainap.pack(side="top")
        
        self.Frequency = tk.Button(self,
                                   width=20,
                                   height=5,
                                   bg="green",
                                   fg = "white")
        self.Frequency["text"] = "Transitions\n of\n Sleep Stage"
        self.Frequency["command"] = self.Frequencies
        self.Frequency.pack(side="top")
            
        #self.quit = tk.Button(self,
        #                      text="Close",
        #                      width=14,
        #                      height=1,
        #                      bg="white",
        #                      fg="black",
        #                      command=self.master.destroy)
        #self.quit.pack(side="bottom")

    def mainapp(self):
        #collect text file
        # Use the for loop to iterate through the list you just created, and open the files

        path = os.getcwd()
        csv_files = glob.glob(os.path.join(path, "*.txt"))

        # loop over the list of csv files
        for f in csv_files:
            d = pd.read_csv(f, skiprows=17, sep='\t', )

            d = d[1:]
            d = d[['Time', 'Stage']]

            d['Time'] = pd.to_datetime(d['Time'], format='%m/%d/%Y %H:%M:%S')
            ##round time
            d['Hour'] = d['Time'].dt.floor(freq='H')

            # Full StageList
            StageList = d[['Stage']]
            StageList = StageList.drop_duplicates()
            StageList['TimeInStage'] = 0
            StageList['key'] = 1

            # list out all of the dates used
            Hours = d[['Hour']]
            Hours = Hours.drop_duplicates()
            Hours['key'] = 1

            StageNotIdentified = pd.merge(Hours, StageList, on='key').drop("key", 1)
            StageNotIdentified = StageNotIdentified.groupby(['Hour', 'Stage']).sum('TimeInStage').reset_index()
            ##count as four seconds for all rows
            d['TimeInStage'] = 4

            d = d.groupby(['Hour', 'Stage']).sum('TimeInStage').reset_index()

            dMerge = d[['Hour', 'Stage']]
            StageNotIdentified = StageNotIdentified[['Hour', 'Stage']]

            outer_join = StageNotIdentified.merge(dMerge, how='outer', indicator=True)
            anti_join = outer_join[~(outer_join._merge == 'both')].drop('_merge', axis=1)
            anti_join['TimeInStage'] = 0

            d = pd.concat([d, anti_join])
            d = d.sort_values(['Hour', 'Stage'])
            d = d.pivot(index='Stage', columns='Hour', values='TimeInStage')

            # output file to match input

            OutputFileName = f.replace('.txt', '')
            file_name = OutputFileName + "Duration" + ".csv"
            d.to_csv(file_name)

    def Frequencies(self):
        path = os.getcwd()
        csv_files = glob.glob(os.path.join(path, "*.txt"))

        for f in csv_files:
            d = pd.read_csv(f, skiprows=17, sep='\t', )
            d = d[1:]
            d = d[['Time', 'Stage']]
            d['Time'] = pd.to_datetime(d['Time'], format='%m/%d/%Y %H:%M:%S')
            ##round time
            d['Hour'] = d['Time'].dt.floor(freq='H')

            # lag stage and if stage is different then record transition
            d['Stage_Lagged'] = d['Stage'].shift(periods=1)
            d['Transition'] = np.where(d['Stage'] != d['Stage_Lagged'], (d['Stage_Lagged'] + '-' + d['Stage']), '')
            # summarize
            d = d.groupby(['Hour', 'Transition']).count().reset_index()
            d["Transition"].replace('', np.nan, inplace=True)
            d.dropna(subset=['Transition'], inplace=True)
            d = d[["Hour", "Transition", "Time"]]
            d = d.rename(columns={'Time': 'N'})

            # dataframe for storing stage combinations
            # NR-R, NR-W, R-NR, R-W, W-NR, W-R
            data = [['NR-R'], ['NR-W'], ['R-NR'], ['R-W'], ['W-NR'], ['W-R']]
            SampleSpace = pd.DataFrame(data, columns=['Transition'])
            hours = d['Hour'].drop_duplicates()
            SampleSpace = SampleSpace.merge(hours, how='cross')

            d['key'] = d['Transition'] + d['Hour'].astype(str)
            SampleSpace['key'] = SampleSpace['Transition'] + SampleSpace['Hour'].astype(str)
            d = SampleSpace.merge(d, on='key', how='left')
            d = d[['Transition_x', 'Hour_x', 'N']]
            d = d.rename(columns={'Transition_x': 'Transition', 'Hour_x': 'Hour'})
            d['N'] = d['N'].fillna(0)
            d = d.sort_values(["Hour", "Transition"])
            d = d.pivot(index='Transition', columns='Hour', values='N')
            # output file to match input

            OutputFileName = f.replace('.txt', '')
            file_name = OutputFileName + "Transition" + ".csv"
            d.to_csv(file_name)

root = tk.Tk()
w = tk.Label(root, text='Use hypnogram txt output.\n Total time recorded in seconds for each stage\n and assumes 4 second bins:')
w.pack()
root.geometry('450x350')
root.title("Hourly Stage Time")
app = Application(master=root)
app.mainloop()
