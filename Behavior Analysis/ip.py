# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 14:18:32 2022

@author: xtcxxx
"""

import pandas as pd 
import numpy as np

res_autocorr = pd.read_csv('res_autocorr.csv', index_col = 0)
trade_size = pd.read_csv('trade_size.csv', index_col = 0)
vol_series = pd.read_csv('vol_series.csv', index_col = 0)
df = res_autocorr.join(trade_size,how= 'inner').join(vol_series,how= 'inner')
'''
import seaborn as sns
sns.pairplot(df)
cor = df.corr()
sns.heatmap(cor, square=True, annot=True)
'''
#阈值确定
delta_p_threshold = np.percentile(df['\delta p autocorr'].dropna(),10)
direction_autocorr_threshold = np.percentile(df['direction autocorr'].dropna(),10)
spread_threshold = np.percentile(df['spread'].dropna(),10)
trade_size_ave_threshold = np.percentile(df['trade_size_ave'].dropna(),90)
trade_size_sum_threshold = np.percentile(df['trade_size_sum'].dropna(),90)
Parks_threshold = np.percentile(df[' Parks'].dropna(),10)
Gk_threshold = np.percentile(df['Gk'].dropna(),10)
#条件满足个数
Suppose = 4
Final = pd.DataFrame()
for i in range(0,len(df)):
    num = 0
    df1 = df.iloc[i]
    if df1['\delta p autocorr'] <= delta_p_threshold:
        num = num + 1
    if df1['direction autocorr'] <= direction_autocorr_threshold:
        num = num + 1
    if df1['spread'] <= spread_threshold:
        num = num + 1
    if df1['trade_size_ave'] >= trade_size_ave_threshold:
        num = num + 1
    if df1['trade_size_sum'] >= trade_size_sum_threshold:
        num = num + 1
    if df1[' Parks'] <= Parks_threshold:
        num = num + 1
    if df1['Gk'] <= Gk_threshold:
        num = num + 1
    if num >= Suppose:
        Final = Final.append(df1)