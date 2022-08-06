# %%
import pandas as pd 
import numpy as np

#generate bond timeseries
def get_y(bond_deal, interval): #bond_deal-此处传入bond_deal.xlsx源数据;  interval--window length, ie. "30T"
    #bond_deal = bond_deal.reset_index()[['TRANSACT_TIME','BEG_DATE','SECURITY_ID','SYMBOL','LATEST_TRANS_PRICE',
                                         #'DIRECTION1','TRADE_VOLUME',"OPEN_PRICE",'WET_AVG_NET_PRICE']]
    ind = (bond_deal['BEG_DATE']<'2022-03-10')&(bond_deal['SYMBOL']=='21国开15')|(bond_deal['BEG_DATE']>='2022-03-10')&(bond_deal['SYMBOL']=='22国开05')
    bond_deal = bond_deal[ind]
    bond_deal['TRANSACT_TIME'] = pd.to_datetime(bond_deal['TRANSACT_TIME'])
    bond_deal.set_index('TRANSACT_TIME', inplace=True)
    bond_deal["VOLUMN*PRICE"] = bond_deal["TRADE_VOLUME"] * bond_deal["OPEN_PRICE"]
    sample = bond_deal.resample(interval,label = 'right')
    #1st price in every window with size=interval 
    open_p = sample.first()["OPEN_PRICE"]
    open_p = open_p.dropna()
    sum = sample.sum()
    avg_p = sum["VOLUMN*PRICE"]/sum['TRADE_VOLUME']
    avg_p = avg_p.dropna()

    return open_p, avg_p 


#example
bond_deal = pd.read_csv('bond_deal.csv')
interval = "30T"
open_p, avg_p = get_y(bond_deal,interval)
#%%
"""
average price = total trade amount /trade volumn in time interval
y1: delta_avg_p: average price at t1 - average price at t0 
y2: average price (starting from t1)
y3: return: (average p t1- average_p t0)/average_p t0
y4: avg_minus_open: average price at t1 - open price at t0 
y5: delta_open_p: open price t1 - open_p t0
y6: delta_avg_p_next: average price at t2 - average price at t1 
y7: return_next:  (average p t2- average_p t1)/average_p t1
"""
y1 = avg_p.diff()
y1 = y1.dropna()
y2 = avg_p.drop(avg_p.index[0])
y3 = y1/avg_p
y3 = y3.dropna()
y4 = y2 - open_p
y4 = y4.dropna()
y5 = open_p.diff().dropna()
y6 = y1.drop(y1.index[0])  
y7 = y5/avg_p.drop(y1.index[0])
y7 = y6.dropna()

Y = pd.DataFrame({"delta_avg_p": y1, " average price": y2,
                  "return": y3, "avg_minus_open":y4, " delta_open_p": y5, "delta_avg_p_next":y6,
                  "return_next": y7
                  })


