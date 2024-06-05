import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy.interpolate import griddata
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
import cartopy.feature as cfeature
from scipy.stats import binned_statistic_2d as histo2D



class Animator():

    def __init__(self, lats=[59, 71], lons=[19, 32], elv=20, daytime=[6, 18]):
        self.lats = lats
        self.lons = lons
        self.elv = elv
        self.daytime = daytime

    def importdf(self, path, save_df=False, filename='processed_data.csv'):
        print('Reading data...')
        if path[-3:] == 'csv':
            df = self.read_data(path)
        else:
            raise ValueError('Error: wrong data file type, only .csv accepted.')
        print('Done.')

        print('Processing data...')
        df = self.process(df)

        if save_df:
            print('Done.')
            print('Saving data...')
            df.to_csv(filename, index=False)
            print(f'Data saved in {filename}.')

        print('All done. Exiting.')

        return df
    
    def animate_pp(self, data, folder='animations', blip=False, filename='pp_animation.gif'):
        print('Creating the animation...')
        if not blip:
            data['datetime'] = data['datetime'].dt.floor('min')

        self.data = data
        self.frames = sorted(self.data['datetime'].unique())

        self.init_animation('pp')

        animation = FuncAnimation(self.fig, self.pp_fig, frames=self.frames[1:], interval=30)

        if folder[-1:] != '/' and len(folder) > 0:
            folder += '/'

        print('Done.')
        print('Saving the animation...')

        animation.save(f'{folder}{filename}', writer='pillow')

        print('All done. Exiting.')



    def read_data(self, path):
        dtypes = {'gps_site': str,
                'sat_id': str,
                'gdlatr': float,
                'gdlonr': float,
                'los_tec': float,
                'tec': float,
                'azm': float,
                'elm': float,
                'gdlat': float,
                'glon': float,
                'gnss_type': str,
                'slant_f': float,
                'vtec': float,
                'pair_id': str,
                'curve_id': int,
                'filtered': float,
                'blrmvd': float}

        raw = pd.read_csv(path, dtype=dtypes)

        raw['datetime'] = pd.to_datetime(raw['datetime'])

        return raw
    

    def process(self, raw):
        data = raw.groupby(['pair_id', 'curve_id']).apply(self.trim_curve).reset_index(drop=True)

        data = data[(data['datetime'].dt.hour >=  self.daytime[0]) & 
                    (data['datetime'].dt.hour < self.daytime[1]) & 
                    (data['elm'] > self.elv)]  
        
        return data

    def trim_curve(self, group):
        group = group.sort_values('datetime')
        start_time = group['datetime'].iloc[0] + timedelta(minutes=15)
        end_time = group['datetime'].iloc[-1] - timedelta(minutes=15)

        return group[(group['datetime'] >= start_time) & (group['datetime'] <= end_time)]





    def init_animation(self, type):
        self.fig, self.ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})

        self.ax.coastlines()
        self.ax.add_feature(cfeature.BORDERS, linestyle=':')
        self.ax.set_xticks(np.arange(self.lons[0], self.lons[1], 1))
        self.ax.set_yticks(np.arange(self.lats[0], self.lats[1]))
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_xlim(self.lons[0], self.lons[1])
        self.ax.set_ylim(self.lats[0], self.lats[1])
        self.ax.set_title(f'Baseline removed VTEC at {self.frames[0]}')

        df0 = self.data.loc[self.data['datetime'] == self.frames[0]]

        if type == 'pp':
            contour = self.ax.scatter(df0['glon'], df0['gdlat'],c= df0['blrmvd'], cmap='plasma', vmin=-2, vmax=2)

        self.fig.subplots_adjust(right=0.8)
        cax = self.fig.add_axes([0.85, 0.155, 0.05, 0.67])

        cbar = plt.colorbar(contour, cax=cax, orientation='vertical',
                            extendrect = True, label='VTEC',
                            ticks=np.arange(-2,2.5,0.5),
                            boundaries = np.arange(-2,2.5,0.5), 
                            extend='both'
        ) 


    def pp_fig(self, frame):
        global ax

        df1 = self.data.loc[self.data['datetime'] == frame]
        self.ax.set_title(f'Baseline removed VTEC at {frame}')

        for c in self.ax.collections:
            c.remove()

        self.ax.scatter(df1['glon'], df1['gdlat'],c= df1['blrmvd'], cmap='plasma', vmin=-2, vmax=2)                

        

        
        
        





















if __name__ == '__main__':

    path = 'data/filtered2013.csv'
    animator = Animator()
    df = animator.importdf(path=path)
    animator.animate_pp(df, folder='')


