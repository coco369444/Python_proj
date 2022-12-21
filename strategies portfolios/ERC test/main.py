# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 17:36:06 2021

@author: cbour
"""
import pandas as pd
import numpy as np


from import_data import get_return,get_cov_inv,get_target_matrix,no_overlap_cov_ret
from mean_variance import get_weights_MV
from ERC import get_weights_ERC,get_weights_RP


start_date="2000-01-01"
end_date = "2020-12-31"
data_ret=get_return(start_date,end_date)

#cov,inv_cov,roll_rets=get_cov_inv(data_ret,period=60)
#target = get_target_matrix(cov)


rets,cov = no_overlap_cov_ret(data_ret,period='1M')


(1+rets).cumprod().plot()
'''
date_i = rets.index[-2]
date_t = rets.index[-1]
cov_i=cov.loc[date_i]
cov_t = cov.loc[date_t]
rets_i=rets.loc[date_i]
rets_t = rets.loc[date_t]

w=get_weights_ERC(cov_i,rets_i)
r=w@rets_t
sig = np.sqrt(w@cov_t@w.T)
sharpe = r/sig
print(w)
print(r)
print(sig)
print(sharpe)


w=get_weights_MV(cov_i,rets_i)
r=w@rets_t
sig = np.sqrt(w@cov_t@w.T)
sharpe = r/sig
print(w)
print(r)
print(sig)
print(sharpe)

w=get_weights_RP(cov_i)
r=w@rets_t
sig = np.sqrt(w@cov_t@w.T)
sharpe = r/sig
print(w)
print(r)
print(sig)
print(sharpe)

rets_t/np.sqrt(np.diag(cov_t))
'''
ERC_ret=[]
MV_ret = []
RP_ret=[]

for i in range(1,len(rets)):
    date_i = rets.index[i-1]
    date_t = rets.index[i]
    cov_i=cov.loc[date_i]
    cov_t = cov.loc[date_t]
    rets_i=rets.loc[date_i]
    rets_t = rets.loc[date_t]

    w_erc=get_weights_ERC(cov_i,rets_i)
    w_mv=get_weights_MV(cov_i,rets_i)
    w_rp=get_weights_RP(cov_i)
    
    ERC_ret.append(w_erc@rets_t)
    MV_ret.append(w_mv@rets_t)
    RP_ret.append(w_rp@rets_t)

ret_test = pd.DataFrame(np.array([ERC_ret,MV_ret,RP_ret]).T,columns=['ERC','MV','RP'])

(1+ret_test).cumprod().plot()

ret_test.mean()*2/ret_test.std()

print(ret_test.mean()*12)
print(ret_test.std()*np.sqrt(12))
