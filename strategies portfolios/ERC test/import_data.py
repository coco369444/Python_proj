# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 16:52:52 2021

@author: cbour
"""

import yfinance as yf
import pandas as pd
import numpy as np


def get_return(start_date,end_date):
    
    snp = yf.Ticker("^GSPC").history(start=start_date, end=end_date)['Close']
    nasdaq = yf.Ticker("^IXIC").history(start=start_date, end=end_date)['Close']
    
    nikkei = yf.Ticker("^N225").history(start=start_date, end=end_date)['Close']
    dow_jones = yf.Ticker("^DJI").history(start=start_date, end=end_date)['Close']
    
    
    names = ['S&P','NASDAQ','DOWJONES']
    
    data_price = pd.concat([snp,nasdaq,dow_jones],axis=1)
    data_price.columns=names
    data_ret = data_price.pct_change(1)
    data_ret.dropna(inplace=True)
    
    return data_ret

def get_cov_inv(data_ret,period=90):
    
    cov = data_ret.rolling(period).cov().dropna()*250
    inv_cov = cov.groupby("Date").apply(lambda g: pd.DataFrame(np.linalg.inv(g.values), index=g.index, columns=g.columns))
    inv_cov.dropna(inplace=True)
    return cov,inv_cov

def no_overlap_cov_ret(data_ret,period='3M'):
    
    rets = (1+data_ret).groupby(pd.Grouper(freq=period)).prod()-1
    cov = data_ret.groupby(pd.Grouper(freq=period)).cov()*250
    return rets,cov


#@nb.jit()
def convert_matrix_vector(matrix):
    
    vector=matrix[0]
    for i in range(1,len(matrix)):
        vector=np.concatenate((vector,matrix[i,i:]))
        
    vector = np.reshape(vector,-1)
    return vector

def get_names_comb(names):
    
    names_exit = []
    for i in range(len(names)):
        for j in range(i,len(names)):
            names_exit.append(f"cov({names[i]},{names[j]})")
    return names_exit

def get_target_matrix(inv_cov):
    date = inv_cov.index.get_level_values(0).drop_duplicates()
    y=[]
    names=inv_cov.columns
    names_cov = get_names_comb(names)
    for d in date:
        inv_cov_i = inv_cov.loc[d]
        
        vector_i = convert_matrix_vector(inv_cov_i.values)
        y.append(vector_i)
        
    target = pd.DataFrame(y,index=date,columns=names_cov)
    return target
    
    
    
    
    
    

