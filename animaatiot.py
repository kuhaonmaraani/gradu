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








    def animate_pp(self, data, folder='animations', blip=False, filename=''):
        print('Creating the pierce point animation...')
        if not blip:
            data['datetime'] = data['datetime'].dt.floor('5min')

        self.data = data
        self.frames = sorted(self.data['datetime'].unique())

        self.init_animation('pp')

        animation = FuncAnimation(self.fig, self.pp_fig, frames=self.frames[1:], interval=80) # type: ignore

        print('Done.')

        if blip and filename == '':
            filename = 'pp_animation_blip.gif'
        elif not blip and filename == '':
            filename = 'pp_animation.gif'

        self.save_ani(animation, folder, filename)

        print('All done. Exiting.')



    def animate_histo(self, data, folder='animations', blip=False, 
                      filename='', res=0.5, method='nearest'):

        print('Creating the histogram animation...')
        if not blip:
            data['datetime'] = data['datetime'].dt.floor('5min')

        self.data = data
        self.frames = sorted(self.data['datetime'].unique())

        self.init_animation('histo')

        animation = FuncAnimation(self.fig, self.histo_fig, frames=self.frames[1:], interval=80) # type: ignore

        print('Done.')

        if blip and filename == '':
            filename = 'histo_animation_blip.gif'
        elif not blip and filename == '':
            filename = 'histo_animation.gif'

        self.save_ani(animation, folder, filename)

        print('All done. Exiting.')



    def animate_griddata(self, data, folder='animations', blip=False, 
                     filename='', res=0.5, method='nearest'):
        print('Creating the griddata animation...')
        if not blip:
            data['datetime'] = data['datetime'].dt.floor('5min')

        self.data = data
        self.frames = sorted(self.data['datetime'].unique())
        self.init_animation('grid', res, method)

        animation = FuncAnimation(self.fig, self.grid_fig, frames=self.frames[1:], interval=80) # type: ignore

        print('Done.')
        if blip and filename == '':
            filename = 'griddata_animation_blip.gif'
        elif not blip and filename == '':
            filename = 'griddata_animation.gif'

        self.save_ani(animation, folder, filename)
        print('All done. Exiting.')



    def animate_all(self, data, folder='animations', blip=False,
                    filenames={'pp':'', 'histo':'', 'grid':''}, res=0.5, method='nearest'):
        
        if not blip:
            data['datetime'] = data['datetime'].dt.floor('5min')

        self.data = data
        self.frames = sorted(self.data['datetime'].unique())
        
        print('Creating the pierce point animation...')
        self.init_animation('pp', res, method)
        animation = FuncAnimation(self.fig, self.pp_fig, frames=self.frames[1:], interval=80) # type: ignore
        print('Done.')
        if blip and filenames['pp'] == '':
            filenames['pp'] = 'pp_animation_blip.gif'
        elif not blip and filenames['pp'] == '':
            filenames['pp'] = 'pp_animation.gif'
        self.save_ani(animation, folder, filenames['pp'])

        plt.close()

        print('Creating the histogram animation...')
        self.init_animation('histo', res, method)
        animation = FuncAnimation(self.fig, self.histo_fig, frames=self.frames[1:], interval=80) # type: ignore
        print('Done.')
        if blip and filenames['histo'] == '':
            filenames['histo'] = 'histo_animation_blip.gif'
        elif not blip and filenames['histo'] == '':
            filenames['histo'] = 'histo_animation.gif'
        self.save_ani(animation, folder, filenames['histo'])

        plt.close()

        print('Creating the griddata animation...')
        self.init_animation('grid', res, method)
        animation = FuncAnimation(self.fig, self.grid_fig, frames=self.frames[1:], interval=80) # type: ignore
        print('Done.')
        if blip and filenames['grid'] == '':
            filenames['histo'] = 'grid_animation_blip.gif'
        elif not blip and filenames['grid'] == '':
            filenames['grid'] = 'grid_animation.gif'
        self.save_ani(animation, folder, filenames['grid'])




        print('All done. Exiting.')





    


    def init_animation(self, type, res=0.5, method='nearest'):
        self.fig, self.ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})

        self.ax.coastlines()
        self.ax.add_feature(cfeature.BORDERS, linestyle=':')
        self.ax.set_xticks(np.arange(self.lons[0], self.lons[1], 1))
        self.ax.set_yticks(np.arange(self.lats[0], self.lats[1]))
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_xlim(self.lons[0], self.lons[1])
        self.ax.set_ylim(self.lats[0], self.lats[1])
        
        df0 = self.data.loc[self.data['datetime'] == self.frames[0]]

        if type == 'pp':
            contour = self.ax.scatter(df0['glon'], df0['gdlat'],c= df0['blrmvd'], cmap='plasma', vmin=-2, vmax=2)
            self.ax.set_title(f'Baseline removed VTEC at {self.frames[0]}')

        elif type == 'histo':
            self.res = res
            self.ax.set_title(f'Baseline removed VTEC at {self.frames[0]} with resolution {res}')
            statistic, x_edges, y_edges, _ = histo2D(
                    df0['glon'], df0['gdlat'], df0['blrmvd'], statistic='mean', 
                    bins=[np.arange(self.lons[0], self.lons[1] + self.res, self.res), 
                          np.arange(self.lats[0], self.lats[1] + self.res, self.res)]) # type: ignore

            X, Y = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2, (y_edges[:-1] + y_edges[1:]) / 2)
            contour = self.ax.pcolormesh(X, Y, statistic.T, cmap='plasma', vmin=-2, vmax=2, 
                                transform=ccrs.PlateCarree())
        elif type == 'grid':
            self.res = res
            self.method = method
            self.ax.set_title(f'Baseline removed binned vtec at {self.frames[0]} \nwith resolution {self.res} and {self.method} method')
            self.x_grid = np.arange(min(self.data['glon']), max(self.data['glon']) + self.res, self.res)
            self.y_grid = np.arange(min(self.data['gdlat']), max(self.data['gdlat']) + self.res, self.res)
            self.X, self.Y = np.meshgrid(self.x_grid, self.y_grid)

            Z = griddata((df0['glon'], df0['gdlat']), df0['blrmvd'], (self.X, self.Y))
            contour = self.ax.pcolormesh(self.x_grid, self.y_grid, Z, cmap='plasma', vmin=-2, vmax=2) 


        self.fig.subplots_adjust(right=0.8)
        cax = self.fig.add_axes([0.85, 0.155, 0.05, 0.67]) # type: ignore

        cbar = plt.colorbar(contour, cax=cax, orientation='vertical',
                            extendrect = True, label='VTEC',
                            ticks=np.arange(-2,2.5,0.5),
                            boundaries = np.arange(-2,2.5,0.5), 
                            extend='both'
        ) 



    def pp_fig(self, frame):

        df1 = self.data.loc[self.data['datetime'] == frame]
        self.ax.set_title(f'Baseline removed VTEC at {frame}')

        for c in self.ax.collections:
            c.remove()

        self.ax.scatter(df1['glon'], df1['gdlat'],c= df1['blrmvd'], cmap='plasma', vmin=-2, vmax=2) 



    def histo_fig(self, frame):

        df1 = self.data.loc[self.data['datetime'] == frame]
        self.ax.set_title(f'Baseline removed VTEC at {frame} with resolution {self.res}')

        statistic, x_edges, y_edges, _ = histo2D(
                    df1['glon'], df1['gdlat'], df1['blrmvd'], statistic='mean', 
                    bins=[np.arange(self.lons[0], self.lons[1] + self.res, self.res), 
                          np.arange(self.lats[0], self.lats[1] + self.res, self.res)]) # type: ignore
        
        X, Y = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2, (y_edges[:-1] + y_edges[1:]) / 2)

        for c in self.ax.collections:
            c.remove()

        self.ax.pcolormesh(X, Y, statistic.T, cmap='plasma', vmin=-2, vmax=2, 
                        transform=ccrs.PlateCarree())



    def grid_fig(self, frame):

        df1 = self.data.loc[self.data['datetime'] == frame]
        self.ax.set_title(f'Baseline removed binned vtec at {frame} \nwith resolution {self.res} and {self.method} method')
        Z = griddata((df1['glon'], df1['gdlat']), df1['blrmvd'], (self.X, self.Y))

        for c in self.ax.collections:
            c.remove()

        self.ax.pcolormesh(self.x_grid, self.y_grid, Z, cmap='plasma', shading='nearest', vmin=-2, vmax=2)                

        

    def save_ani(self, animation, folder, filename):
        if folder[-1:] != '/' and len(folder) > 0:
            folder += '/'

        print('Saving the animation...')

        animation.save(f'{folder}{filename}', writer='pillow')
        print(f'Animation saved in {folder}{filename}.')
        
        
        





if __name__ == '__main__':

    # paths = ['data/filtered20230118.csv',
    #          'data/filtered20230319.csv',
    #          'data/filtered20230321.csv',
    #          'data/filtered20230322.csv',
    #          'data/filtered20231202.csv']

    path = 'data/filtered2017.csv'

    animator = Animator()

    df = animator.importdf(path=path)
    date = path[13:-4]
    filenames = {'pp':f'pp_{date}.gif', 'histo':f'histo_{date}.gif', 'grid':f'grid_{date}.gif'}
    animator.animate_all(df, folder='animations/ready/2017', filenames=filenames)

    # for path in paths:
    #     df = animator.importdf(path=path)
    #     date = path[13:-4]
    #     filenames = {'pp':f'pp_{date}.gif', 'histo':f'histo_{date}.gif', 'grid':f'grid_{date}.gif'}
    #     animator.animate_all(df, folder='animations/ready/2023', filenames=filenames)


