import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import h5py
import pandas as pd
from scipy import signal


class KaariFiltteri():

    def __init__(self, window_lenght=60, polyorder=1):
        # self.lats = lats
        # self.lons = lons
        self.wl = window_lenght
        self.porder = polyorder
        

    def run(self, path, lats=[59, 71], lons=[19, 32], save_df=False):
        
        print('Reading data...')

        if path[-2:] == 'h5':
            df = self.read_data(path, lats, lons)
        elif path[-3:] == 'csv':
            df = pd.read_csv(path)
        else:
            raise ValueError('Error: wrong data file type, only .h5 and .csv accepted.')
        print('Done.')

        if save_df:
            print('Saving data...')
            df.to_csv('filtered_data.csv', index=False)  # Save the DataFrame to a CSV file
            print('Data saved.')

        print('Processing data...')
        df = self.process_data(df)
        print('Done.')
        print('Filtering data...')
        df = self.filter_data(df)
        print('All done.')

        return df

    def read_data(self, path, lats, lons):

        # Access the dataset and filter according to lat and lon ranges
        with h5py.File(path, 'r') as f:
            dset = f['Data']['Table Layout']    # type: ignore
            filtered_data = dset[(dset['gdlonr'] >= min(lons)) & (dset['gdlonr'] <= max(lons)) # type: ignore
                                 & (dset['gdlatr'] >= min(lats)) & (dset['gdlatr'] <= max(lats))]   # type: ignore

        df = pd.DataFrame(filtered_data) # type: ignore

        return df
    
    def calculate_time_diff(self, group):
        time_diff = group['datetime'].diff().dt.total_seconds()
        new_group = time_diff.gt(300).cumsum()
        group['kaari'] = new_group
        
        return group
    
    def process_data(self, df):

        df = df.copy()
        
        # Combine columns to one dtatime column
        df['minute'] = df['min']
        df['second'] = df['sec']
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

        # Pick only needed columns
        df = df[['datetime', 'gps_site', 'sat_id', 'gdlatr', 'gdlonr', 'los_tec', 'tec', 'azm', 'elm', 'gdlat', 'glon', 'gnss_type']]

        # Calculate VTEC from STEC
        df.loc[:, 'slant_f'] = 1 + 16 * (0.53 - df['elm'] / 180) ** 3
        df.loc[:, 'vtec'] = df['los_tec'] / df['slant_f']

        # Create ids for receiver-satellite pairs
        df.loc[:, 'id'] = df['gnss_type'].astype(str) + df['gps_site'].astype(str) + df['sat_id'].astype(str)

        # Apply the function to each group defined by the index
        df = df.groupby('id').apply(self.calculate_time_diff)
        df.reset_index(inplace=True, drop=True) 

        return df
    
    def filter_data(self, df):
        df['filtered'] = signal.savgol_filter(df['tec'], window_length=self.wl, 
                                       polyorder=self.porder, mode="nearest")
        df['blrmvd'] = df['vtec'] - df['filtered']
        
        return df
    
    def plot_kaaret(self, df):

        df.plot('datetime', 'vtec', 'scatter', c='kaari', colormap='plasma')
        plt.xlabel('Datetime')
        plt.ylabel('VTEC')
        plt.title('satelliitti-vastaanotin parin kaaret, laskettu vtec')
        plt.show()
    
    def plot_smoothed(self, df):
        # Plot both lines on the same plot
        plt.plot(df['datetime'], df['vtec'], alpha=0.7, label='VTEC')
        plt.plot(df['datetime'], df['filtered'], label='Filtered')

        # Add labels and legend
        plt.xlabel('Datetime')
        plt.ylabel('Value')
        plt.legend()

        # Show the plot
        plt.show()

    def plot_anomalies(self, df):
        plt.plot(df['datetime'], df['blrmvd'])

        # Add labels and legend
        plt.xlabel('Datetime')
        plt.ylabel('Value')

        # Show the plot
        plt.show()





if __name__ == '__main__':

    path = 'data/filtered_data.csv'
    filtteri = KaariFiltteri()
    df = filtteri.run(path=path)

    idlist = list(df['id'].unique())
    print(df.loc[(df['id'] == idlist[3])]['kaari'].unique())
    df_kaaret = df.loc[df['id'] == idlist[10]]
    df_signaali = df_kaaret.loc[df_kaaret['kaari'] == 0]

    # filtteri.plot_kaaret(df_kaaret)
    # filtteri.plot_anomalies(df_signaali)
    filtteri.plot_smoothed(df_signaali)




