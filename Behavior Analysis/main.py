
# %%
import sys
import os
import pandas as pd
from itertools import count
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from get_feature import Get_x, Get_TF_x
from get_Y import Get_y
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

# %%
#if __name__ == '__main__':

interval = "30min"
bond_deal = pd.read_csv('Data_File/bond_deal.csv')
liquid = bond_deal["SYMBOL"].value_counts()

#21国开15和22国开05 TOP2 liquid
bond_21 = bond_deal[bond_deal["SYMBOL"] == "21国开15"]
bond_22 = bond_deal[bond_deal["SYMBOL"] == "22国开05"] 

# %%
# feature_21 = Get_x(interval,bond_21)
# feature_21 = feature_21.Get_Total().dropna()
# feature_22 = Get_x(interval,bond_22)
# feature_22 =  feature_22.Get_Total().dropna()
# feature_21["instru_id"] , feature_22["instru_id"]  = 1, 2
# feature_21.to_csv("feature_21_"+interval+".csv")
# feature_22.to_csv("feature_22_"+interval+".csv")

# %%
#get label y, 关掉这个file再重新跑， feature_21和y_21不能同时生成
y_21 = Get_y(interval,bond_21)
y_21 = y_21.cal_y().dropna()
y_22 = Get_y(interval,bond_22)
y_22 = y_22.cal_y().dropna()
# %%
# append x and y
feature_21 , feature_22 = pd.read_csv("feature_21_"+interval+".csv"), pd.read_csv("feature_22_"+interval+".csv")
feature_21['TRANSACT_TIME'] = pd.to_datetime(feature_21['TRANSACT_TIME']) #format='%Y%m%d-%H:%M:%S.%j# %%
feature_21.set_index('TRANSACT_TIME',inplace = True)
feature_22['TRANSACT_TIME'] = pd.to_datetime(feature_22['TRANSACT_TIME'])
feature_22.set_index('TRANSACT_TIME',inplace = True)

table_21 = feature_21.join(y_21).dropna()
table_22 = feature_22.join(y_22).dropna()

# %%
#round3:crossectional analysis, sort by time and instrument_id
table = table_21.append(table_22)
table.insert(0,"time",table.index)
table = table.sort_values(by=["time",'instru_id'],ascending=True)

# %%
#round4:add treasure future feature
t , ts, tf= pd.read_csv("Data_File/T2206_1Sec.csv"), pd.read_csv("Data_File/TS2206_1Sec.csv"), pd.read_csv("Data_File/TF2206_1Sec.csv")
feature_t, feature_ts, feature_tf = Get_TF_x(interval,t,".T"), Get_TF_x(interval,ts,'.TS'),Get_TF_x(interval,tf,'.TF')
feature_t, feature_ts, feature_tf = feature_t.get_all(), feature_ts.get_all(), feature_tf.get_all()
table_add_future = table.join(feature_t, how="left").join(feature_ts,how="left").join(feature_tf,how="left").dropna()




# %%
#table = table.reset_index(drop = True)
#table_add_future = table_add_future.reset_index(drop = True)
table = table.set_index(['time','instru_id'],drop=False) #set multiindex
table_add_future = table_add_future.set_index(['time','instru_id'],drop=False)
table.to_csv("crossectional_analysis+_"+interval+".csv")
table_add_future.to_csv("round4_future_"+interval+".csv")



# %%
