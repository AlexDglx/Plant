import os
from glob import glob
import pandas as pd

DIRECTORY = "/Users/adegallaix/Downloads/Headshot Selection"
files = sorted(glob(f'{DIRECTORY}/*.JPG'))
#write in .csv
df = pd.DataFrame(files,columns=["Photo Name"])

df.to_csv("photos_list.csv", index=False)
    
print(len(files))