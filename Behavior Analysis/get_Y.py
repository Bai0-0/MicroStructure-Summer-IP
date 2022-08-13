# %%
import pandas as pd 
import numpy as np

#generate bond timeseries
class Get_y(object):
    def __init__(self,interval,bond_deal) -> None:
        self.interval, self.data = interval, bond_deal
        
    def get_price(self): 
        bond_deal = self.data
        """                                     
        ind = (bond_deal['BEG_DATE']<'2022-03-10')&(bond_deal['SYMBOL']=='21国开15')|(bond_deal['BEG_DATE']>='2022-03-10')&(bond_deal['SYMBOL']=='22国开05')
        bond_deal = bond_deal[ind]
        """
        bond_deal['TRANSACT_TIME'] = pd.to_datetime(bond_deal['TRANSACT_TIME'])
        bond_deal.set_index('TRANSACT_TIME', inplace=True)
        bond_deal["VOLUMN*PRICE"] = bond_deal["TRADE_VOLUME"] * bond_deal["LATEST_TRANS_PRICE"]
        sample = bond_deal.resample(self.interval,label = 'right')
        #1st price in every window with size=interval 
        open_p = sample.first()["LATEST_TRANS_PRICE"]
        open_p = open_p.dropna()
        close_p = sample.last()["LATEST_TRANS_PRICE"]
        close_p = close_p.dropna()
        sum = sample.sum()
        avg_p = sum["VOLUMN*PRICE"]/sum['TRADE_VOLUME']
        avg_p = avg_p.dropna()

        return open_p, avg_p, close_p 

    def cal_y (self):
        """
        average price = total trade amount /trade volumn in time interval
        y1: delta_avg_p: average price at t1 - average price at t0 
        y2: average price (starting from t1)
        y3: return: (average p t1- average_p t0)/average_p t0
        y4: avg_minus_open: average price at t1 - open price at t0 
        y5:delta_open_p : open price t1 - open_price t0

        y6*(new): open_minus_close: open price t1 - last price t0


        y7: delta_avg_p_next: average price at t2 - average price at t1 
        y8: return_next:  (average p t2- average_p t1)/average_p t1
        """
        open_p, avg_p, close_p = self.get_price()
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
                        "return_next": y8
                        })

        return Y




