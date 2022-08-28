'''
Generate feature and y
feature: price autocorrelation, (direction autocorrelation, spread autocorrelation), volatility,
         total trade amount, average trade amount,Timt to future maturity
2022-08-25

When using different bond, switch bond_index,interval ans instID
'''

# %%
from math import nan
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
# %%
df1 = pd.read_csv('table_10min.csv',usecols = ['TIMESTAMP','instID','\delta p autocorr','tradeAmt_avg','tradeAmt_sum','std','TTM'])
df2 = pd.read_csv('table_30min.csv',usecols = ['TIMESTAMP','instID','\delta p autocorr','tradeAmt_avg','tradeAmt_sum','std','TTM'])
# %%
#label：delta average trade volume, delta total trade volume, t1 average trade volumn, t1 total trade volumn
df1['delta_avg_tradevolm'] = df1['tradeAmt_avg'].diff()
df1['delta_sum_tradevolm'] = df1['tradeAmt_sum'].diff()
df1.loc[df1.index[0],'tradeAmt_avg'] = np.nan
df1.loc[df1.index[0],'tradeAmt_sum'] = np.nan
df1.to_csv('volume_table_10min.csv')

df2['delta_avg_tradevolm'] = df2['tradeAmt_avg'].diff()
df2['delta_sum_tradevolm'] = df2['tradeAmt_sum'].diff()
df2.loc[df2.index[0],'tradeAmt_avg'] = np.nan
df2.loc[df2.index[0],'tradeAmt_sum'] = np.nan
df2.to_csv('volume_table_30min.csv')









# %%
