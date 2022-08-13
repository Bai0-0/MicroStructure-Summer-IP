# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 18:26:04 2022

@author: xtcxxx

this file generate x- factor time series, result report to corresponding csv.

"""
# %%
import sys
import os
import pandas as pd
from itertools import count
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)


# %%

class Get_x(object):

  def __init__(self, interval, bond_deal) -> None:
    self.interval, self.data = interval, bond_deal

  #delta_p autocorrelation

  def get_autocorr(self): # 此处传入bond_deal.xlsx源数据

      bond_deal = self.data
      bond_deal = bond_deal.reset_index()[['TRANSACT_TIME','BEG_DATE','SECURITY_ID','SYMBOL','LATEST_TRANS_PRICE','DIRECTION1','TRADE_VOLUME']]
      """
      ind = (bond_deal['BEG_DATE']<'2022-03-10')&(bond_deal['SYMBOL']=='21国开15')|(bond_deal['BEG_DATE']>='2022-03-10')&(bond_deal['SYMBOL']=='22国开05')
      bond_deal = bond_deal[ind]
      """
      bond_deal['TRANSACT_TIME'] = pd.to_datetime(bond_deal['TRANSACT_TIME'])
      bond_deal.set_index('TRANSACT_TIME', inplace=True)

      def f(x):
          # delta p autocorr
          res1 = x['LATEST_TRANS_PRICE'].diff().autocorr(lag=1)
          res2 = ((x['DIRECTION1']-1.5)*2).autocorr(lag=1)
          res3 = x.loc[x['DIRECTION1']==2,'LATEST_TRANS_PRICE'].mean() - x.loc[x['DIRECTION1']==1,'LATEST_TRANS_PRICE'].mean()
          return pd.Series([res1, res2, res3])
      res_table = bond_deal.resample(self.interval, label='right')[['LATEST_TRANS_PRICE','DIRECTION1']].apply(f)
      res_table.rename(columns={0:'\delta p autocorr',1:'direction autocorr',2:'spread'}, inplace=True)
      res_table.dropna(how='all', inplace=True)
      return res_table
      #get_autocorr().to_csv('res_autocorr.csv')

  def get_trade(self): #Average Trade size and total trade amount
    col = ['TRANSACT_TIME', 'LATEST_TRANS_PRICE', 'TRADE_VOLUME', 'SYMBOL']
    df = self.data
    df = df[col]
    trade_time_interval = [9, 18]
    df['trade size'] = df.LATEST_TRANS_PRICE * df.TRADE_VOLUME

    df = df.iloc[:, [0, 3, 4]]
    df.columns = ['TRANSACT_TIME', 'symble', 'sizee']
    df['TRANSACT_TIME'] = pd.to_datetime(df['TRANSACT_TIME'])#format='%Y%m%d-%H:%M:%S.%f'
    df.sort_values(by='TRANSACT_TIME', inplace=True)
    df.set_index(df.TRANSACT_TIME, inplace=True, drop=True)
    df.drop('TRANSACT_TIME', axis=1, inplace=True)
    """
    # 10日之前为’21国开15‘，10日及之后为'22国开05'
    df1 = df[df.index < pd.to_datetime('2022-03-10')]
    df1 = df1[df1.symble == '21国开15']
    df2 = df[df.index >= pd.to_datetime('2022-03-10')]
    df2 = df2[df2.symble == '22国开05']
    # 将前10天和10天之后的DataFrame合并
    df = pd.concat([df1, df2])
    df = df.iloc[:, [1]]
    """

    # 每30分钟交易size的平均值
    tradesize_ave = pd.DataFrame(df.resample(self.interval, label='right').apply(lambda x: x.sizee.mean()))
    tradesize_ave.columns = ['trade_size_ave']
    tradesize_sum = pd.DataFrame(df.resample(self.interval, label='right').apply(lambda x: x.sizee.sum()))
    tradesize_sum.columns = ['trade_size_sum']

    trade_size = pd.concat([tradesize_ave, tradesize_sum], axis=1)

    # 选取交易时间内
    trade_size = trade_size[(trade_size.index.hour >= trade_time_interval[0]) \
                        & (trade_size.index.hour <= trade_time_interval[1]) \
                        & ~((trade_size.index.hour == trade_time_interval[0]) & (trade_size.index.minute == 0)) \
                        & ~((trade_size.index.hour == trade_time_interval[1]) & (trade_size.index.minute == 30))]
    return trade_size


    #trade_size.to_csv('trade_size.csv')
  def get_vol_TTM(self):
    df = self.data
    df['TRANSACT_TIME'] = pd.to_datetime(df['TRANSACT_TIME']) #format='%Y%m%d-%H:%M:%S.%j# %%
    df.set_index('TRANSACT_TIME',inplace = True)
    """
    # drop illiquid bonds
    del1 = df["2022-03-02":"2022-03-09"] 
    del2 = del1[del1["SECURITY_ID"]!= 210215]
    df = df.drop(index = del2.index)
    del3 = df["2022-03-10":]
    del4 = del3[del3["SECURITY_ID"] !=220205]
    df = df.drop(index = del4.index)
    """
    df1 = df

    df1["high_over_low"] = np.log(np.power(df1["HIGHEST_TRANS_PRICE"]/df1["LOWEST_TRANS_PRICE"],2))
    df1["close_over_open"] = np.log(np.power(df1["PRE_CLOSE_NET_PRICE"]/df1["OPEN_PRICE"],2))

    window_data = df1.resample(self.interval,label='right')
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
    vol_series = vol_series.loc[(vol_series != 0).any(axis=1)]

    df2 = df  #BOND Future maturity, lastest ones 0311,0610,assume offset at 9:30 am
    matur1 = "2022-03-11 09:30:00"
    matur2 = "2022-06-10 09:30:00"
    df2["TTM"] = (pd.to_datetime(matur1)-df2.index).days*24*60+(pd.to_datetime(matur1)-df2.index).seconds/60
    df2["TTM"][df2['BEG_DATE'] >matur1 ] =(pd.to_datetime( matur2)-df2.index).days*24*60+(pd.to_datetime( matur2)-df2.index).seconds/60

    res = df2.resample(self.interval,label='right').mean()    #Aaverage time to maturity in the window
    res_TTM = res["TTM"].dropna()
    return vol_series.join(res_TTM,how = "inner")

    #vol_series.to_csv('vol_series.csv')
    #res_TTM.to_csv('res_TTM.csv')

  def Get_Total(self):
    # res_autocorr = pd.read_csv('res_autocorr.csv', index_col = 0)
    # trade_size = pd.read_csv('trade_size.csv', index_col = 0)
    # vol_series = pd.read_csv('vol_series.csv', index_col = 0)
    # res_TTM = pd.read_csv('res_TTM.csv',index_col = 0)
    Total = self.get_autocorr().join(self.get_trade(),how= 'inner').join(self.get_vol_TTM(),how= 'inner')
    #
    
    
    return Total


class Get_TF_x(object):  #create treasure future feature, use ask/bid 1

  def __init__(self, interval, data, instru_id) -> None: #id input string
    self.interval, self.data, self.id = interval, data ,instru_id
  
  def get_all(self): #mid quote volatility
    df1  = self.data.reset_index()[ ['Timestamp', 
       'BidPrice1', 'BidVolume1', 
       'AskPrice1', 'AskVolume1', 
       'OpenPrice', 'ClosePrice',
       'HighestPrice', 'LowestPrice']]
   
     
    df1["Timestamp"] = pd.to_datetime(df1["Timestamp"])
    df1.set_index('Timestamp', inplace=True)

    df1["high_over_low"] = np.log(np.power(df1["HighestPrice"]/df1["LowestPrice"],2))
    df1["close_over_open"] = np.log(np.power(df1["ClosePrice"]/df1["OpenPrice"],2))
    df1["mid_quote"] = (df1.BidPrice1 + df1.AskPrice1)/2
    df1['trade_volume'] = df1.BidPrice1 * df1.BidVolume1 + df1.AskPrice1* df1.AskVolume1

    window = df1.resample(self.interval,label='right')
    count = window.count()["mid_quote"]
    df1_sum = window.sum()
    #Parkinson volatility
    Parks = np.sqrt((1/4*count*np.log(2))*df1_sum["high_over_low"])
    #Garman-Klass 
    Gk = np.sqrt((1/2*count)*df1_sum["high_over_low"]-((2*np.log(2)-1)/count)*df1_sum["close_over_open"])

    vol_series = pd.DataFrame({" Parks":Parks,
                            "Gk": Gk
                            })
    vol_series = vol_series.dropna()
    vol_series = vol_series.loc[(vol_series != 0).any(axis=1)]

    #trade volumn
    avg_volume = df1_sum["trade_volume"]/count
    trade_size = pd.concat( [df1_sum['trade_volume'], avg_volume],axis = 1)
    total = vol_series.join(trade_size).dropna()
    total.columns = ['Parks'+self.id, 'GK'+ self.id, 'trade_volumn'+self.id,'avg_volume'+self.id]
    return total
# %% TEST
# data = pd.read_csv("Data_File/T2206_1Sec.csv")
# T = Get_TF_x("30min",data)
# T = T.get_all()



    








 

# %%
