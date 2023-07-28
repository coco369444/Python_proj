# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 20:28:59 2023

@author: corentin
"""

import requests
import pandas as pd

# from ta.volume import OnBalanceVolumeIndicator
# from ta.momentum import PercentagePriceOscillator
# from ta.volume import ChaikinMoneyFlowIndicator
# from ta.momentum import RSIIndicator, StochasticOscillator

# import ta
import numpy as np




class simulation_strategy():
    
    def __init__(self,ticker='ETHUSDT',interval='2h',look_back_period=3,local=False):
    
        self.path_data = rf"G:\Python Github\Python_proj\Binance_trading/history_base_{ticker}.csv"
        #path = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\Binance_trading"
        
        if local==False:
    
            url = 'https://api.binance.com/api/v3/klines'
            
            start_time = pd.Timestamp("now") - pd.Timedelta(days=look_back_period*365)
            end_time = pd.Timestamp("now")
            df_list = []
            old_start_time=end_time
            
            while old_start_time != start_time:
        
                params = {'symbol': ticker, 'interval': interval, 'startTime': int(start_time.timestamp() * 1000),
                          'endTime': int(end_time.timestamp() * 1000)}
                
                response = requests.get(url, params=params)
                data = response.json()
                df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                                 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                                                 'Taker buy quote asset volume', 'Ignore'])
                df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
                df.set_index('Open time', inplace=True)
                df_list.append(df)
                old_start_time = start_time
                start_time = df.index.max()
                print(start_time)
        
            df = pd.concat(df_list[::-1]).drop_duplicates()
            df=df.iloc[:-1]
            
            df=df[["Close","High","Low","Volume"]].astype(float)
            
        
            df.to_csv(self.path_data)
            
        else : df = pd.read_csv(self.path_data,index_col=0)
        
        df = df.sort_index(ascending=False)
            
        self.raw_data=df.copy()
        self.compute_return_time_period()
        
    def compute_return_time_period(self,train_size=0.8):
        
        returns = self.raw_data["Close"].pct_change(-1)
        
        self.return_train = returns.iloc[int(len(returns)*train_size):]
        self.return_test = returns.iloc[:int(len(returns)*train_size)]
        
        self.df_train = self.raw_data.loc[self.return_train.index]
        self.df_test = self.raw_data.loc[self.return_test.index]
        
    def simulate_strat_train(self,strategy_def,fee=0.01):
        
        self.position=0
        
        position_history = [0]
        pnl=[1]
        
        for i in range(len(self.df_train)):
            df_i = self.df_train.iloc[:i]
            
            new_position = strategy_def(df_i,self.position)
            
            if self.position==new_position:
                new_pnl = pnl[-1]*(1+new_position*self.return_train.iloc[i])
            else :
                new_pnl = pnl[-1]*(1+new_position*self.return_train.iloc[i]-fee)
                
            self.position= new_position
            pnl.append(new_pnl)
            position_history.append(new_position)
        
        self.pnl_train =pnl
        self.positions_train= position_history
            
            
        
        
        
        
        
test = simulation_strategy(local=True)
test.compute_return_time_period()
    