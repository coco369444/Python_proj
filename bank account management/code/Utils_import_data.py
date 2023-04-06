# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 19:18:46 2022

@author: corentin
"""

import numpy as np
import pandas as pd
import os


import re
from datetime import datetime

#path_source = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\bank account management\data"
path_source = r"G:\Python Github\Python_proj\bank account management\data"

def assign_paiment(old_df):
    
    df_category = pd.read_excel((path_source+r"\categorisize_paiment.xlsx").replace("\\","/"))
    categories = []
    for i in range(len(old_df)):
        comand = old_df.iloc[i].lower()
        cat="Other"
        for c in df_category.columns :
            
            if any(ext.lower() in comand for ext in df_category[c].dropna()):
                cat=c
        categories.append(cat)
        
    categories=pd.Series(categories,index=old_df.index)
    
    return categories


def import_bnp_data(path):
    
    data = pd.read_excel(path)  
        
    df_op = data.iloc[2:,:-1]
    df_op.columns = data.iloc[1,:-1]
        
    info_account=data.columns
    
    account_name = info_account[0]
    data_bnp = pd.DataFrame(index=df_op.index)
    data_bnp["category"]=assign_paiment(df_op["Libelle operation"])
    data_bnp["infos"]=df_op["Libelle operation"]
    data_bnp["amount"]=df_op["Montant operation"]
    data_bnp["Date"]= pd.to_datetime(df_op["Date operation"],format='%d-%m-%Y')
        
        
    data_bnp = data_bnp.sort_index(ascending=False)
        
    data_bnp["bank"]="BNP"
    data_bnp["currency"]="EUR"
    
    
    date = info_account[1][9:]
        
    amount_acc = pd.DataFrame([[date,"EUR",info_account[2]]],index=[account_name],columns=["Date","Currency","Amount"])
    amount_acc["bank"]="BNP"
    
    return data_bnp,amount_acc

def import_CS_data(path):
    
    data = pd.read_excel(path)
    df_op = data.iloc[8:-1,:-1]
    df_op.columns = data.iloc[7,:-1]

    date = data.columns[0]
    date_clean = re.search(r'\d{2}.\d{2}.\d{4}', date)
    date = datetime.strptime(date_clean.group(), '%d.%m.%Y')
    acc_name = data.iloc[3,1].partition('\n')[0]
    acc_amount = data.iloc[8,-1]
    info_acc = pd.DataFrame([[date,"CHF",acc_amount]],index=[acc_name],columns=["Date","Currency","Amount"])
    info_acc["bank"]="CS"
    
    data_date = df_op["Date comptable"]
    date_pre = data_date.loc[data_date!="Prénotages"].iloc[0]
    data_date=pd.to_datetime(data_date.replace("Prénotages",date_pre),format='%d.%m.%Y')
    data_cs = pd.DataFrame(index=df_op.index)
    data_cs["category"]=assign_paiment(df_op["Texte"])
    data_cs["infos"]=df_op["Texte"]
    data_cs["Date"]=data_date
    data_cs["Date"]= pd.to_datetime(data_cs["Date"])
    data_cs["amount"]=df_op["Crédit"].fillna(0) - df_op["Débit"].fillna(0) 
    data_cs["bank"]="CS"
    data_cs["currency"]="CHF"
    
    return data_cs,info_acc


def import_Revolut_data(path):

    data = pd.read_csv(path)
    amount = data.iloc[-1,-1]
    date=data["Completed Date"].iloc[-1]
    currency = data["Currency"].iloc[-1]
    acc_info = pd.DataFrame([[date,currency,amount]],index=[f"Revolut {currency}"],columns=["Date","Currency","Amount"])
    acc_info["bank"]="Revolut"
    
    data_revolut = pd.DataFrame(index=data.index)
    data_revolut["category"]=assign_paiment(data["Description"])
    data_revolut["infos"]=data["Description"]
    data["Completed Date"]=data["Completed Date"].fillna(datetime.now().strftime('%Y-%m-%d'))
    data_revolut["Date"]= data["Completed Date"]
    data_revolut["amount"]=data["Amount"]
    data_revolut["bank"]="Revolut"
    data_revolut["currency"]=currency
    
    return data_revolut,acc_info

def import_JB_data(path):
    data = pd.read_csv(path,sep=";")
    amount = data.iloc[0,5].replace("'",'')
    date_start=data.iloc[0,1]
    currency = data.columns[5][6:]
    acc_info = pd.DataFrame([[date_start,currency,amount]],index=[f"JB {currency}"],columns=["Date","Currency","Amount"])
    acc_info["bank"]="JB"
    data_JB =pd.DataFrame(index=data.index)
    
    data_JB["category"]=assign_paiment(data["Texte de l'écriture"])
    data_JB["infos"]=data["Texte de l'écriture"]
    date = data["Date de valeur"]
    
    
    data_JB["Date"]= pd.to_datetime(date,format='%d.%m.%Y')
    data_JB["amount"]=data["Crédit"].str.replace("'",'').astype(float).fillna(0) - data["Débit"].str.replace("'",'').astype(float).fillna(0)
    data_JB["bank"]= "JB"
    data_JB["currency"]= currency
    
    return data_JB,acc_info







