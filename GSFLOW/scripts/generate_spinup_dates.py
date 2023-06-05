import os
import pandas as pd
from datetime import datetime


# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")


dates = pd.date_range(start="1980-01-02", end="2015-12-30")
df = pd.DataFrame({'dates': dates})
df['year'] = -999
df['month'] = -999
df['day'] = -999
df['year'] = df['dates'].dt.year
df['month'] = df['dates'].dt.month
df['day'] = df['dates'].dt.day
df['dates_str'] = df['dates'].astype(str)
df['dates_str'] = '#' + df['dates_str']

file_path = os.path.join(script_ws, 'script_outputs', 'spinup_dates.csv')
df.to_csv(file_path)