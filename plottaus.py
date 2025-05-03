import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.impute import SimpleImputer


# Load the CSV files into a list of DataFrames
data_dir = "data/keog"
imp_dir = 'data/imp/'
og_dir = 'data/og/'


for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        try:
            df = pd.read_csv(os.path.join(data_dir, file))

            title = f'{df["datetime"][0][:10]}'

            XX, YY = np.meshgrid(df['time_seconds'].unique(),df['gdlat'].unique())
            ZZ = df['blrmvd'].values
            ZZ = np.reshape(ZZ,XX.T.shape).T


            fig = plt.figure()
            img = plt.pcolormesh(XX, YY, ZZ, cmap='plasma')
            plt.title(title)

            plt.savefig(f'{og_dir}{title}og.png')
            #plt.show()
            

            imputer = SimpleImputer(strategy='mean')
            ZZimp = imputer.fit_transform(ZZ)
            plt.close()
            fig = plt.figure()
            
            plt.pcolormesh(XX, YY, ZZimp, cmap='plasma')
            plt.title(title)

            plt.savefig(f'{imp_dir}{title}imp.png')
            #plt.show()
            plt.close()

        except:
            print(f'Error with {file}')
            plt.show()
            plt.close()
            continue


