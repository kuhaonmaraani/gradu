import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import h5py
import pandas as pd
from scipy import signal
from datetime import timedelta


class KaariFiltteri():

    def __init__(self, window_lenght=60, polyorder=1):
        self.wl = window_lenght
        self.porder = polyorder
        

    def importdf(self, path, lats=[59, 71], lons=[19, 32], save_df=False, 
                 filename='filtered_data.csv', paiva=[6,16], min_el=20):
        
        print('Reading data...')

        if path[-2:] == 'h5':
            df = self.read_data(path, lats, lons, paiva, min_el)
        elif path[-3:] == 'csv':
            df = pd.read_csv(path)
        else:
            raise ValueError('Error: wrong data file type, only .h5 and .csv accepted.')
        print('Done.')

        print('Processing data...')
        df = self.process_data(df)
        print('Done.')

        print('Filtering data...')
        df = self.filter_data(df)
        print('Done.')

        print('Trimming the curves...')
        df = self.process2(df)
        df = df[['datetime', 'gdlat', 'glon', 'blrmvd']] ##SÄÄDÄ OUTPUT SARAKKEET

        if save_df:
            print('Done.')

            print('Saving data...')
            df.to_csv(filename, index=False)
            print(f'Data saved in {filename}.')
        
        print('All done. Exiting.')

        return df
    
    def read_data(self, path, lats, lons, paiva, min_el):
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        min_hour, max_hour = min(paiva), max(paiva)

        with h5py.File(path, 'r') as f:
            dset = f['Data']['Table Layout']    # type: ignore
            # Read the necessary columns only
            data = np.array(dset)
        
            # Apply the filters
            mask = (
                (data['gdlonr'] >= min_lon) & (data['gdlonr'] <= max_lon) &
                (data['gdlatr'] >= min_lat) & (data['gdlatr'] <= max_lat) &
                (data['hour'] >= min_hour) & (data['hour'] <= max_hour) &
                (data['elm'] >= min_el)
                )
        
            filtered_data = data[mask]

        df = pd.DataFrame(filtered_data)  # type: ignore

        return df
    
    def calculate_time_diff(self, group): #separates satellite-receiver pair curves
        time_diff = group['datetime'].diff().dt.total_seconds()
        new_group = time_diff.gt(300).cumsum()
        group['curve_id'] = new_group
        
        return group
    
    def process_data(self, ogdf):

        df = ogdf.copy()

            
        # Combine columns to one datetime column
        try:
            df['minute'] = df['min']
            df['second'] = df['sec']
            df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
        except:
            raise IndexError('The needed datetime columns not found. Please, make sure that the data contains the following columns: year, month, day, hour, minute and second')
        
        columns = ['datetime', 'gps_site', 'sat_id', 'los_tec', 'tec', 'elm', 'gdlat', 'glon', 'gnss_type']

        # Check if the needed columns are in the dataframe
        for column in columns:
            if column not in df:
                print(f'WARNING: the dataframe doesnt have a column called {column}. A column of zeros will be created.')
                df[column] = 0

        # Pick only needed columns
        df = df[columns]

        # Calculate VTEC from STEC
        df.loc[:, 'slant_f'] = 1 + 16 * (0.53 - df['elm'] / 180) ** 3
        df.loc[:, 'vtec'] = df['los_tec'] / df['slant_f']

        # Create ids for receiver-satellite pairs
        df.loc[:, 'pair_id'] = df['gnss_type'].astype(str) + df['gps_site'].astype(str) + df['sat_id'].astype(str)

        # Apply the function to each group defined by the index
        df = df.groupby('pair_id').apply(self.calculate_time_diff)
        df.reset_index(inplace=True, drop=True) 

        return df
    
    def filter_data(self, df):
        df['filtered'] = signal.savgol_filter(df['tec'], window_length=self.wl, 
                                       polyorder=self.porder, mode="nearest")
        df['blrmvd'] = df['vtec'] - df['filtered']
        
        return df
    
    def process2(self, df): 
        
        df['datetime'] = pd.to_datetime(df['datetime'])

        data = df.groupby(['pair_id', 'curve_id']).apply(self.trim_curve).reset_index(drop=True)
        data['datetime'] = data['datetime'].dt.floor('5min')

        return data
    

    def trim_curve(self, group):
        group = group.sort_values('datetime')
        start_time = group['datetime'].iloc[0] + timedelta(minutes=15)
        end_time = group['datetime'].iloc[-1] - timedelta(minutes=15)

        return group[(group['datetime'] >= start_time) & (group['datetime'] <= end_time)]    














    
    def plot_kaaret(self, df):

        df.plot('datetime', 'vtec', 'scatter', c='curve_id', colormap='plasma')
        plt.xlabel('Datetime')
        plt.ylabel('VTEC')
        plt.title('satelliitti-vastaanotin parin kaaret, laskettu vtec')
        plt.show()
    
    def plot_smoothed(self, df):
     
        plt.plot(df['datetime'], df['vtec'], alpha=0.7, label='VTEC')
        plt.plot(df['datetime'], df['filtered'], label='Filtered')

        plt.xlabel('Datetime')
        plt.ylabel('Value')
        plt.legend()

        plt.show()

    def plot_anomalies(self, df):
        plt.plot(df['datetime'], df['blrmvd'])

        plt.xlabel('Datetime')
        plt.ylabel('Value')

        plt.show()










if __name__ == '__main__':

    path = 'data/los/los_20230319.001.h5'
    filtteri = KaariFiltteri()
    df = filtteri.importdf(path=path, save_df=True, filename='testi.csv')

    # idlist = list(df['pair_id'].unique())
    # print(df.loc[(df['id'] == idlist[3])]['curve_id'].unique())
    # df_kaaret = df.loc[df['pair_id'] == idlist[10]]
    # df_signaali = df_kaaret.loc[df_kaaret['curve_id'] == 0]

    # filtteri.plot_kaaret(df_kaaret)
    # filtteri.plot_anomalies(df_signaali)
    # filtteri.plot_smoothed(df_signaali)




