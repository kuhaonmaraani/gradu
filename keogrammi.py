import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d as histo2D



class Keogram():

    def __init__(self, long=25, res=1, lats = [57,66], timeres=300):
        self.long = long
        self.minlon = long-1
        self.maxlon = long+2
        self.res = res
        self.minlat = min(lats)
        self.maxlat = max(lats)
        self.timeres = timeres

    def run_csv(self, path, savename='', savepath=''):
        if path[-4:] != '.csv':
            raise ImportError('Wrong data file type. Only .csv files accepted.')
        
        if (len(savename) > 4) & (savename[-4:] != '.csv'):
            raise TypeError('Savename value invalid. Must be of the form name.csv.')
        
        
        #print('Reading data...')

        
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])


        #print('Done.')
        #print('Applying mask...')


        mask = ((df['glon'] >= self.minlon) & 
                (df['glon'] <= self.maxlon) &
                (df['gdlat'] >= self.minlat) & 
                (df['gdlat'] <= self.maxlat))
        df = df[mask]

        df1 = df.loc[(df['glon'] >= self.long) & (df['glon'] <= self.long+1)]


        #print('Done.')
        #print('Processing data...')


        reference_time = df1['datetime'].min()
        df1['time_seconds'] = (df1['datetime'] - reference_time).dt.total_seconds()

        time_bin_edges = np.arange(0, df1['time_seconds'].max() + self.timeres, self.timeres)  # 5 minutes in seconds
        latitude_bin_edges = np.arange(df1['gdlat'].min(), df1['gdlat'].max() + self.res, self.res)

        self.statistic, x_edges, y_edges, _ = histo2D(
            df1['time_seconds'], df1['gdlat'], df1['blrmvd'], statistic='mean',
            bins=[time_bin_edges, latitude_bin_edges]) # type:ignore

        self.X, self.Y = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2, (y_edges[:-1] + y_edges[1:]) / 2)


        #print('Done.')
        #print('Saving data...')
        
        x_flat = self.X.flatten()
        y_flat = self.Y.flatten()
        z_flat = self.statistic.flatten()

        binned_data_df = pd.DataFrame({
            'time_seconds': x_flat,
            'gdlat': y_flat,
            'blrmvd': z_flat
        })

        reference_time = df1['datetime'].min()
        binned_data_df['datetime'] = pd.to_timedelta(binned_data_df['time_seconds']-150, unit='s') + reference_time
        
        
        self.DATETIME = df.iloc[0]['datetime'].date()
        
        if savename == '':
            self.string = str(self.DATETIME).replace('-','')
            savename = f'keogram{self.string}long{self.long}.csv'
         
        savename = savepath+savename

        binned_data_df.to_csv(savename, index=False)

        print(f'Data saved at {savename}.')
        #print('All done. Exiting...')





    def run_df(self, df, savename='', savepath=''):
  
        #print('Reading data...')

        df['datetime'] = pd.to_datetime(df['datetime'])


        #print('Done.')
        #print('Applying mask...')


        mask = ((df['glon'] >= self.minlon) & 
                (df['glon'] <= self.maxlon) &
                (df['gdlat'] >= self.minlat) & 
                (df['gdlat'] <= self.maxlat))
        df = df[mask]

        df1 = df.loc[(df['glon'] >= self.long) & (df['glon'] <= self.long+1)]


        #print('Done.')
        #print('Processing data...')


        reference_time = df1['datetime'].min()
        df1['time_seconds'] = (df1['datetime'] - reference_time).dt.total_seconds()

        time_bin_edges = np.arange(0, df1['time_seconds'].max() + self.timeres, self.timeres)
        latitude_bin_edges = np.arange(df1['gdlat'].min(), df1['gdlat'].max() + self.res, self.res)

        self.statistic, x_edges, y_edges, _ = histo2D(
            df1['time_seconds'], df1['gdlat'], df1['blrmvd'], statistic='mean',
            bins=[time_bin_edges, latitude_bin_edges]) # type:ignore

        self.X, self.Y = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2, (y_edges[:-1] + y_edges[1:]) / 2)


        #print('Done.')
        #print('Saving data...')
        
        x_flat = self.X.flatten()
        y_flat = self.Y.flatten()
        z_flat = self.statistic.flatten()

        binned_data_df = pd.DataFrame({
            'time_seconds': x_flat,
            'gdlat': y_flat,
            'blrmvd': z_flat
        })

        reference_time = df1['datetime'].min()
        binned_data_df['datetime'] = pd.to_timedelta(binned_data_df['time_seconds']-150, unit='s') + reference_time
        
        
        self.DATETIME = df.iloc[0]['datetime'].date()
        
        if savename == '':
            self.string = str(self.DATETIME).replace('-','')
            savename = f'keogram{self.string}long{self.long}.csv'
         
        savename = savepath+savename

        binned_data_df.to_csv(savename, index=False)

        print(f'Data saved at {savename}.')
        #print('All done. Exiting...')







    
    
    def plot(self, save=False, show=True, savepath=''):

        print('Plotting...')

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_title(f'Baseline removed VTEC at longitude {self.long}')
        ax.set_ylabel('Latitude')
        ax.set_xlabel('Datetime')

        contour = ax.pcolormesh(self.X, self.Y, self.statistic.T, cmap='plasma')

        fig.subplots_adjust(right=0.8)
        cax = fig.add_axes([0.85, 0.155, 0.05, 0.67]) # type: ignore

        cbar = plt.colorbar(contour, cax=cax, orientation='vertical',label='VTEC')

        

        if save == True:
            print('Done.')
            print('Saving the plot...')
            if savepath == '':
                savepath = f'keogram{self.string}long{self.long}.png'
            plt.savefig(savepath)

        if show == True:
            print('Done')
            print('Showing the plot...')
            plt.show()
        
        print('All done. Exiting..')




if __name__ == '__main__':

    path = 'testi.csv'
    keogram = Keogram()
    keogram.run_csv(path)

    keogram.plot()








