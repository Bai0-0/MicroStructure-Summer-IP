# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 18:26:04 2022

@author: xtcxxx

this file generate x- factor time series, result report to corresponding csv.

"""
import pandas as pd
bond_deal = pd.read_excel('bond_deal.xlsx')
def get_autocorr(interval='30min',
                 bond_deal=bond_deal  # 此处传入bond_deal.xlsx源数据
                ):
    # data manipulation
    bond_deal = bond_deal.reset_index()[['TRANSACT_TIME','BEG_DATE','SECURITY_ID','SYMBOL','LATEST_TRANS_PRICE','DIRECTION1','TRADE_VOLUME']]
    ind = (bond_deal['BEG_DATE']<'2022-03-10')&(bond_deal['SYMBOL']=='21国开15')|(bond_deal['BEG_DATE']>='2022-03-10')&(bond_deal['SYMBOL']=='22国开05')
    bond_deal = bond_deal[ind]

    bond_deal['TRANSACT_TIME'] = pd.to_datetime(bond_deal['TRANSACT_TIME'])
    bond_deal.set_index('TRANSACT_TIME', inplace=True)
    def f(x):
        # delta p autocorr
        res1 = x['LATEST_TRANS_PRICE'].diff().autocorr(lag=1)
        res2 = ((x['DIRECTION1']-1.5)*2).autocorr(lag=1)
        res3 = x.loc[x['DIRECTION1']==2,'LATEST_TRANS_PRICE'].mean() - x.loc[x['DIRECTION1']==1,'LATEST_TRANS_PRICE'].mean()
        return pd.Series([res1, res2, res3])
    res_table = bond_deal.resample(interval, label='right')[['LATEST_TRANS_PRICE','DIRECTION1']].apply(f)
    res_table.rename(columns={0:'\delta p autocorr',1:'direction autocorr',2:'spread'}, inplace=True)
    res_table.dropna(how='all', inplace=True)
    return res_table
get_autocorr().to_csv('res_autocorr.csv')


#%%
interval = '30min'
data_path = 'Bond_Deal.xlsx'
col = ['TRANSACT_TIME', 'LATEST_TRANS_PRICE', 'TRADE_VOLUME', 'SYMBOL']
trade_time_interval = [9, 18]

data = pd.read_excel(data_path)
df = data[col]
df['trade size'] = df.LATEST_TRANS_PRICE * df.TRADE_VOLUME

df = df.iloc[:, [0, 3, 4]]
df.columns = ['TRANSACT_TIME', 'symble', 'sizee']

df.TRANSACT_TIME = pd.to_datetime(df.TRANSACT_TIME, format='%Y%m%d-%H:%M:%S.%f')
df.sort_values(by='TRANSACT_TIME', inplace=True)
df.set_index(df.TRANSACT_TIME, inplace=True, drop=True)
df.drop('TRANSACT_TIME', axis=1, inplace=True)

# 10日之前为’21国开15‘，10日及之后为'22国开05'
df1 = df[df.index < pd.to_datetime('2022-03-10')]
df1 = df1[df1.symble == '21国开15']
df2 = df[df.index >= pd.to_datetime('2022-03-10')]
df2 = df2[df2.symble == '22国开05']
# 将前10天和10天之后的DataFrame合并
df = pd.concat([df1, df2])
df = df.iloc[:, [1]]

# 每30分钟交易size的平均值
tradesize_ave = pd.DataFrame(df.resample(interval, label='right').apply(lambda x: x.sizee.mean()))
tradesize_ave.columns = ['trade_size_ave']
tradesize_sum = pd.DataFrame(df.resample(interval, label='right').apply(lambda x: x.sizee.sum()))
tradesize_sum.columns = ['trade_size_sum']

trade_size = pd.concat([tradesize_ave, tradesize_sum], axis=1)

# 选取交易时间内
trade_size = trade_size[(trade_size.index.hour >= trade_time_interval[0]) \
                        & (trade_size.index.hour <= trade_time_interval[1]) \
                        & ~((trade_size.index.hour == trade_time_interval[0]) & (trade_size.index.minute == 0)) \
                        & ~((trade_size.index.hour == trade_time_interval[1]) & (trade_size.index.minute == 30))]


trade_size.to_csv('trade_size.csv')
# %% data processing
interval = "30T"
from itertools import count
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_csv('Bond_Deal.csv')

df['TRANSACT_TIME'] = pd.to_datetime(df['TRANSACT_TIME']) #format='%Y%m%d-%H:%M:%S.%j# %%
df.set_index('TRANSACT_TIME',inplace = True)

# drop illiquid bonds
del1 = df["2022-03-02":"2022-03-09"] 
del2 = del1[del1["SECURITY_ID"]!= 210215]
df = df.drop(index = del2.index)
del3 = df["2022-03-10":]
del4 = del3[del3["SECURITY_ID"] !=220205]
df = df.drop(index = del4.index)
df.to_csv("bond_deal_result.csv")

df1 = df

df1["high_over_low"] = np.log(np.power(df1["HIGHEST_TRANS_PRICE"]/df1["LOWEST_TRANS_PRICE"],2))
df1["close_over_open"] = np.log(np.power(df1["PRE_CLOSE_NET_PRICE"]/df1["OPEN_PRICE"],2))



#Volatility
#T means minutes
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



#BOND Future maturity, lastest ones 0311,0610,assume offset at 9:30 am
df2 = df
matur1 = "2022-03-11 09:30:00"
matur2 = "2022-06-10 09:30:00"
df2["TTM"] = (pd.to_datetime(matur1)-df2.index).days*24*60+(pd.to_datetime(matur1)-df2.index).seconds/60
df2["TTM"][df2['BEG_DATE'] >matur1 ] =(pd.to_datetime( matur2)-df2.index).days*24*60+(pd.to_datetime( matur2)-df2.index).seconds/60



  #T means minutes
res = df2.resample(interval,label='right').mean()    #Aaverage time to maturity in the window
res_TTM = res["TTM"].dropna()
vol_series.to_csv('vol_series.csv')
res_TTM.to_csv('res_TTM.csv')
#%%
res_autocorr = pd.read_csv('res_autocorr.csv', index_col = 0)
trade_size = pd.read_csv('trade_size.csv', index_col = 0)
vol_series = pd.read_csv('vol_series.csv', index_col = 0)
res_TTM = pd.read_csv('res_TTM.csv',index_col = 0)
#%%
Total = res_autocorr.join(trade_size,how= 'inner').join(vol_series,how= 'inner').join(res_TTM,how= 'inner')
