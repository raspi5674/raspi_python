# this code written in python 3

# SQLITE CODE TO SET UP HEALTH TABLE:
# CREATE TABLE "weight" ( date TEXT PRIMARY KEY, weight REAL, bf_pcnt REAL );
# 

import sqlite3
import pandas as pd
from pandas.io import sql
import datetime
import math

initial_data = pd.read_csv("AggWeightData.csv")
data = initial_data.dropna(thresh=2)

# do some sum checking to validate all data came over ok and we didn't drop any
wtsum = data["weight"].dropna().sum()
# 99930.81
bfpcntsum = data["bf_pcnt"].dropna().sum()
# 2855.4
# today_string = datetime.date.today().strftime("%Y-%m-%d")
conn = sqlite3.connect("health.db")
cur = conn.cursor()

# this line doesn't work exactly as I'd want, so don't use it
# data.to_sql('health',conn)

for i in range(data.shape[0]):
   yr = data.values[i][0][6:10]
   mth = data.values[i][0][0:2]
   day = data.values[i][0][3:5]
   recdate = yr + "-" + mth + "-" + day
   
   wt = data.values[i][1]
   bfpcnt = data.values[i][2]
   if math.isnan(bfpcnt):
      bfpcnt = "NULL"
   
   command = "INSERT INTO weight VALUES ('%s',%s,%s);" % (recdate, wt, bfpcnt)
   cur.execute(command)

conn.commit


# do some checking to make sure it all made it in ok
cur.execute("select sum(weight) from weight;)
cur.fetchall()
# 99930.81
cur.execute("select sum(bf_pcnt) from weight;")
cur.fetchall()
# 2855.4

cur.close()
conn.close()


