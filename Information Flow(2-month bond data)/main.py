'''
Generate feature and y
feature: price autocorrelation, (direction autocorrelation, spread autocorrelation), volatility,
         total trade amount, average trade amount,Timt to future maturity
2022-08-25

When using different bond, switch bond_index,interval ans instID
'''

# %%
from operator import concat
from pickle import FALSE
import sys
import os
from tokenize import Ignore
import pandas as pd
from itertools import count
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
# %%
#merge all bond trade data
bond_index = '190215' #19国开10 190210;  190205; 190215
data = pd.read_csv("Bond trade data/2019-20.csv",usecols=["PRICE","TRDDATE","TRDTIME","I_CODE","TRDFV","TRDCASHAMT","DIRCTION"])
data = data[data.I_CODE==bond_index] 
for i in range(19,0,-1):
    df = pd.read_csv("Bond trade data/2019-"+ str(i) +".csv",usecols=["PRICE","TRDDATE","TRDTIME","I_CODE","TRDFV","TRDCASHAMT","DIRCTION"])
    df = df[df.I_CODE==bond_index]
    data = pd.concat([data,df],axis = 0,ignore_index=True)
data['TIMESTAMP'] = data["TRDDATE"] +"  " +data["TRDTIME"]
data["TIMESTAMP"]=pd.to_datetime(data.TIMESTAMP)
data.set_index(data.TIMESTAMP, inplace=True, drop=True)
#data['DIRCTION'] = data['DIRCTION'].map({'F':1, 'J':2},na_action=None)
#df["DIRCTION"].value_counts()
    
# %%
'''
generate_feature
'''
interval = "10min" 
matur1 = "2019-09-13 18:30:00" #BOND Future maturity, assume offset at 18:30 
matur2 = "2019-12-13 18:30:00"
data["TTM"] = (pd.to_datetime(matur1)-data.index).days*24*60+(pd.to_datetime(matur1)-data.index).seconds/60
data['TTM'][data.index> matur1]=(pd.to_datetime( matur2)-data.index).days*24*60+(pd.to_datetime( matur2)-data.index).seconds/60

def f(x):
    res1 = x['PRICE'].diff().autocorr(lag=1)
    res2 = x['TRDFV'].mean()
    res3 = x['TRDFV'].sum()
    res4 = x['PRICE'].std()
    res5 = x['TTM'].mean()
    return pd.Series([res1, res2, res3, res4, res5])

res_table = data.resample(interval, label='right')[['PRICE','TRDFV','TTM']].apply(f)
res_table.rename(columns={0:'\delta p autocorr',1:'tradeAmt_avg',2:'tradeAmt_sum',3:'std',4:'TTM'}, inplace=True)
res_table = res_table.dropna()
# %%
'''
generate y
'''
sample = data.resample(interval,label = 'right')
#1st price in every window with size=interval 
open_p = sample.first()["PRICE"]
open_p = open_p.dropna()
close_p = sample.last()["PRICE"]
close_p = close_p.dropna()
sum = sample.sum()
avg_p = sample.mean()['PRICE']
avg_p = avg_p.dropna()

       
# y1: delta_avg_p: average price at t1 - average price at t0 
# y2: average price (starting from t1)
# y3: return: (average p t1- average_p t0)/average_p t0
# y4: avg_minus_open: average price at t1 - open price at t0 
# y5:delta_open_p : open price t1 - open_price t0

# y6*(new): open_minus_close: open price t1 - last price t0


# y7: delta_avg_p_next: average price at t2 - average price at t1 
# y8: return_next:  (average p t2- average_p t1)/average_p t1
y1 = avg_p.diff()
y1 = y1.dropna()
y2 = avg_p.drop(avg_p.index[0])
y3 = y1/avg_p
y3 = y3.dropna()
y4 = y2 - open_p
y4 = y4.dropna()
open = open_p
y5 = open.diff().dropna()
y6 = open_p.drop(open_p.index[0]) - close_p.drop(close_p.index[len(close_p)-1])
y7 = y1.drop(y1.index[0])  
y8 = (y7/y2)
y8 = y8.dropna()

Y = pd.DataFrame({"delta_avg_p": y1, " average price": y2,
            "return": y3, "avg_minus_open":y4, " delta_open_p": y5, "open_minus_close" : y6,
            "delta_avg_p_next":y7,
            "return_next": y8})

# %%
#merge feature and y, index=TIMESTAMP
instID = 3
feature_y_table = res_table.join(Y,how ='inner').drop(res_table.index[0])
feature_y_table.insert(0,"instID",instID)
feature_y_table.to_csv('feature & y _'+bond_index+"_"+interval+'.csv')

# %%
#Combine different bond as crossectional
df, df1, df2 = pd.read_csv('feature & y _190210_10min.csv'), pd.read_csv('feature & y _190205_10min.csv'), pd.read_csv('feature & y _190215_10min.csv')
table_10min = pd.concat([df,df1,df2], axis=0,ignore_index=True)
table_10min = table_10min.set_index(['TIMESTAMP','instID'],drop = True)
table_10min.to_csv('table_10min.csv')

# %%
df, df1, df2 = pd.read_csv('feature & y _190210_30min.csv'), pd.read_csv('feature & y _190205_30min.csv'), pd.read_csv('feature & y _190215_30min.csv')
table_30min = pd.concat([df,df1,df2], axis=0,ignore_index=True)
table_30min = table_30min.set_index(['TIMESTAMP','instID'],drop = True)
table_30min.to_csv('table_30min.csv')




# %%
