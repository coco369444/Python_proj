# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 08:50:11 2022

@author: corentin
"""

import numpy as np
import pandas as pd
import os
from Utils_import_data import import_bnp_data,import_CS_data,import_Revolut_data,import_JB_data




paths =[(r"D:\Corentin\Bureau\bank account management\data\BNP").replace("\\","/"),
        (r"D:\Corentin\Bureau\bank account management\data\CS").replace("\\","/"),
        (r"D:\Corentin\Bureau\bank account management\data\Revolut").replace("\\","/"),
        (r"D:\Corentin\Bureau\bank account management\data\JB").replace("\\","/"),
        ]

functions_data = [import_bnp_data,import_CS_data,import_Revolut_data,import_JB_data]

df_operations=pd.DataFrame()
df_accounts=pd.DataFrame()
for i in range(len(paths)) :
    
    path = paths[i]
    xls_names = [ name for name in os.listdir(path) if not os.path.isdir(os.path.join(path, name)) ]
    get_data_func = functions_data[i]
    for name in xls_names :
        df_op_i,df_acc_i = get_data_func(path+f"/{name}")
    
        df_operations=pd.concat((df_operations,df_op_i))
        df_accounts=pd.concat((df_accounts,df_acc_i))

df_operations["Date"]=pd.to_datetime(df_operations["Date"],format="%Y-%m-%d")
df_operations.to_csv((r"D:\Corentin\Bureau\bank account management\data\data_operations.xlsx").replace("\\","/"),index=False)
df_accounts.to_csv((r"D:\Corentin\Bureau\bank account management\data\data_accounts.xlsx").replace("\\","/"),index=False)

