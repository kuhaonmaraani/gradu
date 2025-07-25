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
            title2 = f'dTEC keogram date {df["datetime"][0][:10]} longitude 25◦E'

            XX, YY = np.meshgrid(df['time_seconds'].unique(),df['gdlat'].unique())
            ZZ = df['blrmvd'].values
            ZZ = np.reshape(ZZ,XX.T.shape).T


            fig = plt.figure(figsize=(10,8))
            img = plt.pcolormesh(XX, YY, ZZ, cmap='plasma', vmin=-2, vmax=2)
            plt.title(title2, fontsize=20)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=16)
            plt.ylabel('Latitude (◦N)', fontsize=20)
            plt.xlabel('Time (seconds, starting from 6:00 UTC)', fontsize=20)

            cbar = plt.colorbar(img,
                       extendrect = True,
                        ticks=np.arange(-2,2.5,0.5),
                        boundaries = np.arange(-2,2.5,0.5), 
                        extend='both'
            )

            cbar.set_label('dTEC (TECU)', fontsize=20)
            cbar.ax.tick_params(labelsize=16)

            plt.tight_layout()
            plt.savefig(f'{og_dir}{title}og.png')
            #plt.show()
            
            

            imputer = SimpleImputer(strategy='mean')
            ZZimp = imputer.fit_transform(ZZ)
            plt.close()
            fig = plt.figure()
            
            plt.pcolormesh(XX, YY, ZZimp, cmap='plasma', vmin=-2, vmax=2)
            plt.title(title2, fontsize=20)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=16)
            plt.ylabel('Latitude (◦N)', fontsize=20)
            plt.xlabel('Time (seconds, starting from 6:00 UTC)', fontsize=20)

            cbar = plt.colorbar(img,
                       extendrect = True,
                        ticks=np.arange(-2,2.5,0.5),
                        boundaries = np.arange(-2,2.5,0.5), 
                        extend='both'
            )

            cbar.set_label('dTEC (TECU)', fontsize=20)
            cbar.ax.tick_params(labelsize=16)

            plt.tight_layout()
            plt.savefig(f'{imp_dir}{title}imp.png')
            #plt.show()
            plt.close()

        except:
            print(f'Error with {file}')
            plt.show()
            plt.close()
            continue


