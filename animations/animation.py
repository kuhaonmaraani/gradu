import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
import io
from PIL import Image



paths = ('data/gps230120g002.hdf5', 'data/gps230121g002.hdf5', 'data/gps230122g002.hdf5')

LAT = [55,75]
LONG = [0,30]
WINDOW_HOURS = 1.5



#Read the files to one dataframe

print('Reading the data files......')

df =pd.DataFrame()

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

df = df.loc[(df['gdlat'] >= LAT[0]) & (df['gdlat'] <= LAT[1]) & (df['glon'] >= LONG[0]) & (df['glon'] <= LONG[1])]
df = df.sort_values(by=['gdlat', 'datetime'], ascending=True)

print('Done')

#calculate the rolling mean

print('Calculating the rolling mean.....')

rolling_df = pd.DataFrame()

for long in df['glon'].unique():
    for lat in df['gdlat'].unique():
        df5 = df.loc[(df['gdlat'] == lat) & (df['glon'] == long)]
        moving_avg = df5['tec'].rolling(window=int(12*WINDOW_HOURS), min_periods=1, center=True).mean()
        rolling_df = pd.concat([rolling_df, moving_avg], axis=0)



#add detrended tec to the data dataframe

df = pd.concat([df, rolling_df], axis=1)
df['rolling'] = df[0]
df = df.drop(columns=[0])
df['detrended_tec'] = df['tec'] - df['rolling']

print('Done')

#create figures functions

def create_fig(datetime, df):
    plt.figure(figsize=(8, 6))
    dff = df.loc[df['datetime'] == datetime]
    pivot = dff.pivot('gdlat', 'glon', 'detrended_tec')

    sns.heatmap(pivot, cmap='viridis',vmin=-4, vmax=4)
    # plt.axvline(x=20.53, color='black', lw=3)
    plt.gca().invert_yaxis()

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Baseline removed TEC Heatmap at {datetime}')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    heatmap_array = np.array(Image.open(buf))
    return heatmap_array

def update(frame, df=df):
    heatmap = create_fig(frame, df)
    plt.clf()
    plt.imshow(heatmap)


print('Creating the animation. this may take a while.......')

#create an animation out of figures

frames = sorted(df['datetime'].unique())
fig, ax = plt.subplots()

# Create the animation using ArtistAnimation
animation = FuncAnimation(fig, update, frames=frames, interval=100)

# Save the animation as a GIF file
#animation.save('heatmap_animation.gif', writer='imagemagick')

# Save the animation as an MP4 file (requires ffmpeg or avconv installed)
animation.save(f'animations/heatmap_animation_{WINDOW_HOURS}H.mp4', writer='ffmpeg')

































