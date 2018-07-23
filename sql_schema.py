# this code written in python 3

import sqlite3
import pandas as pd
from pandas.io import sql
import datetime

data = pd.read_csv("AggWeightData")
today_string = datetime.date.today().strftime("%Y-%m-%d")
conn = sqlite3.connect("health.db")
cur = conn.cursor()

# this line doesn't work exactly as I'd want, so don't use it
# data.to_sql('health',conn)

for i in range(data.shape[0]):
    
    yr  = data.values[i][0][3:5]
    mth = data.values[i][0][0:2]
    day = data.values[i][0][6:10]
    day.strftime("%Y-%m-%d")
    command = "INSERT INTO weight VALUES ('"
    command  = command + YYYY-MM-DD',225.0,NULL)"



cur.close()
conn.close()
