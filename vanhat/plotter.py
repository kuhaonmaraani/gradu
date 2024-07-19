import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy.stats import binned_statistic_2d as histo2D





class Plotter():

    def __init__(self, elv=20, daytime=[6, 18]):
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
    







    
    def plot_lat(self, df, lat, save = False, filename='', folder=''):
        df1 = df.loc[df['gdlat'] == lat]
        df1['datetime'] = df1['datetime'].dt.floor('5min')

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Longitude')
        ax.set_title(f'Baseline removed VTEC at {lat} latitude')

        statistic, x_edges, y_edges, _ = histo2D(
                    df1['datetime'], df1['glon'], df1['blrmvd'], statistic='mean') # type: ignore
        
        X, Y = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2, (y_edges[:-1] + y_edges[1:]) / 2)

        ax.pcolormesh(X, Y, statistic.T, cmap='plasma', vmin=-2, vmax=2)

        plt.show()


        


    def plot_lon(self):
        pass
    def plot_pixel(self):
        pass



























if __name__ == '__main__':
    path = 'data/filtered20230118.csv'

    plotter = Plotter()
    df = plotter. importdf(path=path)
    plotter.plot_lat(df, 61)











