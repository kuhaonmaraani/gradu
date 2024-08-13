import pandas as pd
import numpy as np

# Define the date range
start_date = pd.to_datetime('2018-01-01')
end_date = pd.to_datetime('2023-01-06')

# Generate all dates within the range
all_dates = pd.date_range(start_date, end_date)

# Divide dates by seasons
seasons = {
    "winter": [],
    "spring": [],
    "summer": [],
    "fall": []
}

for date in all_dates:
    year = date.year
    # Northern hemisphere seasons
    if date.month in [12, 1, 2]:
        seasons["winter"].append(date)
    elif date.month in [3, 4, 5]:
        seasons["spring"].append(date)
    elif date.month in [6, 7, 8]:
        seasons["summer"].append(date)
    elif date.month in [9, 10, 11]:
        seasons["fall"].append(date)

# Choose random dates from each season ensuring all years are represented
np.random.seed(42)  # For reproducibility
selected_dates = []

for season, dates in seasons.items():
    df = pd.DataFrame({"dates": dates})
    df['year'] = df['dates'].dt.year
    
    selected_per_year = df.groupby('year').apply(lambda x: x.sample(min(40, len(x)))).reset_index(drop=True)
    selected_dates.extend(selected_per_year['dates'])

# Randomly shuffle the selected dates and pick 160
np.random.shuffle(selected_dates)
selected_dates = sorted(selected_dates[:160])

for date in sorted(selected_dates):
    print(date)
