import os
import glob
import keogrammi
import kaariproc

folder_path = 'data/los/'

files = glob.glob(os.path.join(folder_path, '*.h5'))

filtteri = kaariproc.KaariFiltteri()
keogram = keogrammi.Keogram()

i = 1

for path in files:
    print(f"Processing file: {path}")
    df = filtteri.importdf(path=path, save_df=False, lats=[56,71])
    
    print(f'Creating the keogram for {path}')
    keogram.run_df(df, savepath='data/keog/')
    print(f'Processing done. {len(files)-i} files to go, progress: {i/len(files)*100:.2f}%')
    i += 1

print('All done.')
    

