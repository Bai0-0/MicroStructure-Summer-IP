
# %% data processing
from itertools import count
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
# %%
df = pd.read_csv('Bond_Deal_0731.csv')

df['Datetime'] = pd.to_datetime(df['TRANSACT_TIME']) #format='%Y%m%d-%H:%M:%S.%j# %%
df.set_index("Datetime",inplace = True)
# %%
# drop illiquid bonds
del1 = df["2022-03-02":"2022-03-09"] 
del2 = del1[del1["SECURITY_ID"]!= 210215]
df = df.drop(index = del2.index)
del3 = df["2022-03-10":]
del4 = del3[del3["SECURITY_ID"] !=220205]
df = df.drop(index = del4.index)
df.to_csv("bond_deal_result.csv")

# %%
df1 = df

df1["high_over_low"] = np.log(np.power(df1["HIGHEST_TRANS_PRICE"]/df1["LOWEST_TRANS_PRICE"],2))
df1["close_over_open"] = np.log(np.power(df1["PRE_CLOSE_NET_PRICE"]/df1["OPEN_PRICE"],2))


# %%
#Volatility
interval = "30T"   #T means minutes
window_data = df1.resample(interval,label='right')
count = window_data.count()["BEG_DATE"]
df1_sum = window_data.sum()
#Parkinson volatility
Parks = np.sqrt((1/4*count*np.log(2))*df1_sum["high_over_low"])

#Garman-Klass 
Gk = np.sqrt((1/2*count)*df1_sum["high_over_low"]-((2*np.log(2)-1)/count)*df1_sum["close_over_open"])

vol_series = pd.DataFrame({" Parks":Parks,
                         "Gk": Gk
                         })
vol_series = vol_series.dropna()
vol_series =  vol_series.loc[(vol_series != 0).any(axis=1)]
# a = a = vol_series["20220301"]
# plt.plot(a)
# plt.xticks(rotation = 300)
# plt.show()


