# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 20:46:53 2021

@author: cbour
"""
import pandas as pd
import numpy as np

from scipy.optimize import minimize

def optim(x,cov):
    return x@cov@x.T



def get_weights_MV(cov,rets):
    
    x0=np.ones(len(rets))/len(rets)
    
    def constraint_1(x):
        return x
    
    def constraint_2(x):
        return sum(x)-1
    
    cons=({'type': 'ineq', 'fun': constraint_1},
          {'type': 'eq', 'fun': constraint_2})
    
    res = minimize(optim,x0,args=cov,constraints=cons)
    
    return res.x

