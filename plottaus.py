import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.impute import SimpleImputer


# Load the CSV files into a list of DataFrames
data_dir = "data/keog/"
imp_dir = 'data/imp/'
og_dir = 'data/og/'

for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join(data_dir, file))
        title = f'{df['datetime'][0][:10]}'
        pivot_df = df.pivot(index='gdlat', columns='time_seconds', values='blrmvd')
        
        imputer = SimpleImputer(strategy='mean')
        impdf = imputer.fit_transform(pivot_df)

        fig = plt.figure()
        time_grid, lat_grid = np.meshgrid(pivot_df.columns.values, pivot_df.index.values)
        plt.pcolormesh(time_grid, lat_grid, impdf)
        plt.title(title)
        plt.gca().invert_yaxis()

        plt.savefig(f'{imp_dir}{title}imp.png')
        #plt.show()
        plt.close()

     


        fig = plt.figure()
        img = plt.pcolormesh(time_grid, lat_grid, pivot_df.values)
        plt.title(title)
        plt.gca().invert_yaxis()

        plt.savefig(f'{og_dir}{title}og.png')
        #plt.show()
        plt.close()

