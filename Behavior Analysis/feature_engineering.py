# %%
import pandas as pd
import numpy as np
import warnings
import os

# feature engineering
# 1. bond feature engineering
y_col = ['delta_avg_p', ' average price', 'return', 'avg_minus_open',
       ' delta_open_p', 'open_minus_close', 'delta_avg_p_next', 'return_next']
data = pd.read_csv('crossectional_analysis+_10min.csv',index_col=0)
data = data.reset_index().set_index(['time','instru_id']).drop(columns='time.1').rename(columns={'\delta p autocorr':'delta p autocorr'})
data_instru1 = data.loc[:,1,:].copy()

data_instru2 = data.loc[:,2,:].copy()
data_instru1
#%%
def feature_engineering(data):
    X_data = data.drop(columns=y_col)
    y_data = data[y_col].copy()
    data = data[y_data.columns.to_list()+X_data.columns.to_list()]
    data_all = data.copy()
    for lag in range(1,5):
        data_all = data_all.merge(X_data.shift(lag), left_index=True, right_index=True, suffixes=['',f'_lag{lag}'])

    data_all = data_all.merge(X_data.diff(1), left_index=True, right_index=True, suffixes=['',f'_diff'])
    data_all = data_all.merge(X_data.diff(2), left_index=True, right_index=True, suffixes=['',f'_diff2'])
    data_all = data_all.merge(y_data.shift(1), left_index=True, right_index=True, suffixes=['',f'_y_lag1'])


    ind = data_all.corr().loc['delta_avg_p'].abs().gt(0.08)
    ind[y_col] = True
    # print(data_all.corr().loc['delta_avg_p',ind])
    return data_all.loc[:,ind]
data_instru1_f = feature_engineering(data_instru1)
data_instru2_f = feature_engineering(data_instru2)

data_instru1_f['instru_id_is2'] = False
data_instru2_f['instru_id_is2'] = True
col_list = y_col+list((set(data_instru1_f.columns.to_list())&set(data_instru2_f.columns.to_list()))-set(y_col))+['instru_id_is2']
data_f = pd.concat([data_instru1_f[col_list],data_instru2_f[col_list]])
data_f.shape

#%%
data_f.to_csv('bond_feature_and_y_crossectional_10min.csv')

#%%

# 2. bond and future
data = pd.read_csv('round4_future_10min.csv', index_col=0)
data.reset_index()
#%%
data = data.reset_index().set_index(['time','instru_id']).drop(columns='time.1').rename(columns={'\delta p autocorr':'delta p autocorr'})
data_instru1 = data.loc[:,1,:].copy()
data_instru2 = data.loc[:,2,:].copy()
data_instru1
#%%
def feature_engineering(data):
    X_data = data.drop(columns=y_col)
    y_data = data[y_col].copy()
    data = data[y_data.columns.to_list()+X_data.columns.to_list()]
    data_all = data.copy()
    for lag in range(1,5):
        data_all = data_all.merge(X_data.shift(lag), left_index=True, right_index=True, suffixes=['',f'_lag{lag}'])

    data_all = data_all.merge(X_data.diff(1), left_index=True, right_index=True, suffixes=['',f'_diff'])
    data_all = data_all.merge(X_data.diff(2), left_index=True, right_index=True, suffixes=['',f'_diff2'])
    data_all = data_all.merge(y_data.shift(1), left_index=True, right_index=True, suffixes=['',f'_y_lag1'])

    ind = data_all.corr().loc['delta_avg_p'].abs().gt(0.08)
    ind[y_col] = True
    # print(data_all.corr().loc['delta_avg_p',ind])
    return data_all.loc[:,ind]
data_instru1_f = feature_engineering(data_instru1)
data_instru2_f = feature_engineering(data_instru2)

data_instru1_f['instru_id_is2'] = False
data_instru2_f['instru_id_is2'] = True
col_list = y_col+list((set(data_instru1_f.columns.to_list())&set(data_instru2_f.columns.to_list()))-set(y_col))+['instru_id_is2']
data_f = pd.concat([data_instru1_f[col_list],data_instru2_f[col_list]])
data_f
#%%
data_f.to_csv('bond_future_feature_and_y_crossectional_10min.csv')