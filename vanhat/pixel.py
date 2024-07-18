import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


# LAT, LON = [55,70], [11,23] #RUOTSI
# LAT, LON = [65,69], [14,23] #NORRA NORRLAND
# LAT, LON = [61,65], [12,22] #SÖDRA NORRLAND
# LAT, LON = [59,61], [11,19] #SVEALAND
# LAT, LON = [55,59], [11,17] #GÖTALAND

LAT = [65,69]
LONG = 20
WINDOW_HOURS = 4
DT1, DT2 = '2023-01-20 00:00:00', '2023-01-23 00:00:00'

path = 'data/gps230120g002.hdf5'



#Read the files to one dataframe


file = h5py.File(path, 'r')
dataset = file['Data'].get('Table Layout') # type: ignore
data_array = np.array(dataset)
file.close()

df1 = pd.DataFrame(data_array)

df1['minute'] = df1['min']
df1['second'] = df1['sec']
df1['datetime'] = pd.to_datetime(df1[['year', 'month', 'day', 'hour', 'minute', 'second']])
df1 = df1.drop(['recno','kindat','kinst','ut1_unix','ut2_unix', 'year', 'month', 'day', 'hour', 'minute', 'second', 'min', 'sec'], axis=1)


df1 = df1.loc[(df1['gdlat'] >= LAT[0]) & (df1['gdlat'] <= LAT[1]) & (df1['glon'] == LONG)]
df1 = df1.sort_values(by=['gdlat', 'datetime'], ascending=True)
df1['plt_date'] = mdates.date2num(df1['datetime']) # type: ignore


rolling_df = pd.DataFrame()

print('Calculating the rolling mean........')

for long in df1['glon'].unique():
    for lat in df1['gdlat'].unique():
        df5 = df1.loc[(df1['gdlat'] == lat) & (df1['glon'] == long)]
        moving_avg = df5['tec'].rolling(window=12*WINDOW_HOURS, min_periods=1, center=True).mean()
        rolling_df = pd.concat([rolling_df, moving_avg], axis=0)



#add detrended tec to the data dataframe

df1 = pd.concat([df1, rolling_df], axis=1)
df1['rolling'] = df1[0]
df1 = df1.drop(columns=[0])
df1['detrended_tec'] = df1['tec'] - df1['rolling']


#first plot

print('Creating the first plot......')

fig, ax = plt.subplots()

pivot1 = df1.pivot('gdlat', 'datetime', 'tec') #type: ignore
#sns.heatmap(pivot1, cmap='viridis', ax=ax)
ax.pcolormesh(pivot1)

# ax.set_xlabel('Datetime')
# ax.set_ylabel('Latitude')
ax.set_title(f'TEC Heatmap for longitude {LONG}')
#ax.invert_yaxis()

# Set the x-axis major locator and formatter
# plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

plt.tight_layout()

plt.show()
plt.close()
