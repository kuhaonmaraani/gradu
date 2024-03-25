import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

paths = ('data/gps230120g002.hdf5', 'data/gps230121g002.hdf5', 'data/gps230122g002.hdf5')

# pathi95 = 'data/ruots/gotaland.csv'
pathi95 = 'data/ruots/norra_norrland.csv'
# pathi95 = 'data/ruots/sodra_norrland.csv'
# pathi95 = 'data/ruots/svealand.csv'





#Read the files to one dataframe

df =pd.DataFrame()

print('Reading data files.....')

for path in paths:
    file = h5py.File(path, 'r')
    dataset = file['Data'].get('Table Layout') # type: ignore
    data_array = np.array(dataset)
    file.close()

    df1 = pd.DataFrame(data_array)

    df1['minute'] = df1['min']
    df1['second'] = df1['sec']
    df1['datetime'] = pd.to_datetime(df1[['year', 'month', 'day', 'hour', 'minute', 'second']])
    df1 = df1.drop(['recno','kindat','kinst','ut1_unix','ut2_unix', 'year', 'month', 'day', 'hour', 'minute', 'second', 'min', 'sec'], axis=1)
    df = pd.concat([df, df1], axis=0, ignore_index=True)

df = df.loc[(df['gdlat'] >= LAT[0]) & (df['gdlat'] <= LAT[1]) & (df['glon'] == LONG)]
df = df.sort_values(by=['gdlat', 'datetime'], ascending=True)
df['datetime'] = pd.to_datetime(df['datetime'])

print('Done')

#calculate the rolling mean

rolling_df = pd.DataFrame()

print('Calculating the rolling mean........')

for long in df['glon'].unique():
    for lat in df['gdlat'].unique():
        df5 = df.loc[(df['gdlat'] == lat) & (df['glon'] == long)]
        moving_avg = df5['tec'].rolling(window=12*WINDOW_HOURS, min_periods=1, center=True).mean()
        rolling_df = pd.concat([rolling_df, moving_avg], axis=0)



#add detrended tec to the data dataframe

df = pd.concat([df, rolling_df], axis=1)
df['rolling'] = df[0]
df = df.drop(columns=[0])
df['detrended_tec'] = df['tec'] - df['rolling']
df['detrended_tec'].describe()

print('Done')



#first plot

print('Creating the first plot......')

pivot1 = df.pivot('gdlat', 'datetime', 'tec') #type: ignore
pivot1.columns = mdates.date2num(pivot1.columns)
sns.heatmap(pivot1, cmap='viridis')

plt.xlabel('Datetime')
plt.ylabel('Latitude')
plt.title(f'TEC Heatmap for longitude {LONG}')
plt.gca().invert_yaxis()
# plt.xticks(rotation = 0)

# Set the x-axis major locator and formatter
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
plt.gca().xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator(interval_multiples=True)))

plt.tight_layout()

plt.show()
plt.close()

print('Done')


# #I95 data

# print('Reading the I95 data.......')

# dfi95 = pd.read_csv(pathi95, header=None, sep=';')

# dfi95['datetime'] = pd.to_datetime(dfi95[0])
# dfi95['i95'] = dfi95[1].str.replace(',', '.').astype(float)
# dfi95.drop([0, 1], axis=1, inplace=True)
# dfi95 = dfi95.loc[(dfi95['datetime'] >= DT1) & (dfi95['datetime'] <= DT2)]

# print('Done')
# print('Creating the second plot.......')

# #second plot

# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(111)

# pivot = df.pivot('gdlat', 'datetime', 'detrended_tec') #type: ignore

# min_x = df['datetime'].min()
# max_x = df['datetime'].max()

# ax.set_xlim(min_x, max_x)
# g1 = sns.heatmap(pivot, cmap='viridis', vmin=-4, vmax=4, ax=ax, cbar=False)
# ax.invert_yaxis()
# g1.set(xlabel=None, ylabel = 'Latitude', title = f'Baseline removed TEC Heatmap for longitude {LONG} and a line plot for I95')
# ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)



# ax2 = fig.add_subplot(111)
# ax2.plot(dfi95['datetime'], dfi95['i95'], color='white', zorder=10, lw=3)
# ax2.yaxis.set_label_text('I95')
# plt.xticks(rotation = 0)
# ax2.set_xlim(min_x, max_x)
# ax2.yaxis.tick_right()
# ax2.grid(False)
# ax2.patch.set_alpha(0.0) #type: ignore
# ax2.spines['top'].set_visible(False)
# ax2.spines['right'].set_visible(False)
# ax2.spines['bottom'].set_visible(False)
# ax2.spines['left'].set_visible(False)
# ax2.yaxis.set_label_position("right")


# # Set the date format to display only the date (e.g., "YYYY-MM-DD")
# ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H'))

# plt.tight_layout()

# plt.show()
















