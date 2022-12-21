# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:30:31 2022

@author: corentin
"""
import numpy as np
import pandas as pd
from get_data_binance import getdailydata,create_TS
from optuna_model import trading_bot
import optuna

data_source_ETH=getdailydata("ETHUSDT")
X3,index_data,ret=create_TS(data_source_ETH,TS_lenght=25)

#data_source_BTC=getdailydata("BTCUSDT")
#X1,_,_=create_TS(data_source_BTC)

#data_source_XRP=getdailydata("ADAUSDT")
#X2,_,_=create_TS(data_source_XRP)

#X = np.concatenate((X3,X1,X2),axis=2)
X=X3
train_size=0.9
validation_size = 0.2

trading_bot_ETH = trading_bot(X,ret,index_data,train_size,validation_size)
n_trials=100
trading_bot_ETH.find_good_model(n_trials)




optuna.visualization.plot_intermediate_values(trading_bot_ETH.study)
