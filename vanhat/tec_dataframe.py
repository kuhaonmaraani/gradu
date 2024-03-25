import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import json

LONG = 25
data_dir = 'data/tomo/numeric_result/*.json' 


# Create an empty list to store filtered DataFrames
filtered_dfs = []
index=1

# Iterate through all files in the directory
for file_path in glob.glob(data_dir):
    pros=(index/len(glob.glob(data_dir))*100) 
    
    with open(file_path, 'r') as f:

        data = json.load(f)
        df = pd.DataFrame(
            {'lat': data['lat'], 
            'alt': data['alt'],
            'ne': data['ne'],
            'long': data['long']
            })
        df = df.loc[df['long'] == LONG]
        df=df.drop(columns=['long'])
        df['datetime'] = data['t_end'][0]
        
        # Add the filtered DataFrame to the list
        filtered_dfs.append(df)

        index += 1
    print(f'Reading files... {pros:2f}% done', end='\r')


# Concatenate the filtered DataFrames into a single DataFrame
result_df = pd.concat(filtered_dfs, ignore_index=True)

# Select the desired columns
result_df = result_df[['ne', 'datetime', 'lat']]

# Display the resulting DataFrame
print(result_df.head(5))













