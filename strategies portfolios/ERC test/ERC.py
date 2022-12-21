# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 10:25:22 2021

@author: cbour
"""
import pandas as pd
import numpy as np

from scipy.optimize import minimize

def optim(x,cov):
    vol_i = cov@x.T
    f=0
    for i in range(len(x)):
        for j in range(len(x)):
            f+=(x[i]*vol_i[i]-x[j]*vol_i[j])**2
    
    return f



def get_weights_ERC(cov,rets):
    
    x0=np.ones(len(rets))
    
    def constraint_1(x):
        return x
    
    def constraint_2(x):
        return np.sum(x)-1
    
    cons=({'type': 'ineq', 'fun': constraint_1},
          {'type': 'eq', 'fun': constraint_2})
    
    res = minimize(optim,x0,args=(cov),constraints=cons)
    
    return res.x

def get_weights_RP(cov):
    sigg=1/np.diag(cov)
    
    w = sigg/sum(sigg)
    return w
    
    
    
    
