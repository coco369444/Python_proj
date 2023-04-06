# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 19:55:44 2023

@author: corentin
"""

import numpy as np
import pandas as pd
import datetime


path_source = r"G:\Python Github\Python_proj\bank account management\data"

account_data=pd.read_csv(path_source+"/data_accounts.csv")
operations = pd.read_excel(path_source+"/data_operations.xlsx")


bank=["CS"]

currency ="CHF"


data_op_i = operations.loc[(operations["bank"]== bank[0]) & (operations["currency"]==currency)]

amount_base,date_base = account_data.loc[(account_data["bank"]==bank[0]) & (account_data["Currency"]==currency)][["Amount","Date"]].values[0]

date_base=datetime.datetime.strptime(date_base,"%Y-%m-%d %H:%M:%S")


data_op_2i = data_op_i[["amount","Date"]]
data_op_2i["amount"]=data_op_2i["amount"]*-1
data_op_2i.loc[len(data_op_2i)]=[amount_base,date_base]
data_op_group=data_op_2i.groupby("Date").sum()

data_op_group = data_op_group.sort_index(ascending=False)

data_op_cumsum=data_op_group.cumsum()

data_op_cumsum.plot()


