
# %% data processing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

df1 = pd.read_csv('bond_deal_result.csv',index_col = "Datetime")



    
df1["high_over_low"] = np.log(np.power(df1["HIGHEST_TRANS_PRICE"]/df1["LOWEST_TRANS_PRICE"],2))
df1["close_over_open"] = np.log(np.power(df1["PRE_CLOSE_NET_PRICE"]/df1["OPEN_PRICE"],2))
# %%
interval = "30T"   #T-minutes
window_data = df1.resample(interval)






# %%



