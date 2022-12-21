# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 19:06:31 2022

@author: corentin
"""
import pandas as pd
import numpy as np
import os

import re
from datetime import datetime

path = (r"D:\Corentin\Bureau\bank account management\data\JB_bourse").replace("\\","/")
xls_name = [ name for name in os.listdir(path) if not os.path.isdir(os.path.join(path, name)) ][0]
path_csv = path+"/"+xls_name

data = pd.read_csv(path_csv,sep=";")
data = data.loc[data["État"]=="Exécuté"]
data = data[["Instrument","Quantité","Dev","Modifié"]]
data["Instrument"]=data["Instrument"].str.replace('UNITS','')
data["Instrument"]=data["Instrument"].str.replace('UNIT','')
data["Instrument"]=data["Instrument"].str.replace('"','')
data["Instrument"]=data["Instrument"].str.lstrip()
data["Modifié"]=pd.to_datetime(data['Modifié'], format='%d.%m.%Y %H:%M').dt.date
data.columns = ["Instrument","Quantity","Currency","Date"]


path_excel = (r"D:\Corentin\Bureau\bank account management\data\JB_stock_exchange.xlsx").replace("\\","/")
#data.to_excel(path_excel,index=False)

data_isin = pd.read_excel(path_excel)
list_instru = data_isin["Instrument"].values
data_new = data.loc[~data["Instrument"].isin(list_instru)]

data_tot = pd.concat((data_isin,data_new))
data_tot.to_excel(path_excel,index=False)
