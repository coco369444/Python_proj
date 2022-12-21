# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:28:35 2022

@author: corentin
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils

from binance import Client
client=Client()

def getdailydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,"4h","3 years ago UTC"))
    frame=frame[[0,1,2,3,4,5,8]]
    frame.columns=["Timestamp","Open","High","Low","Close","Volume","Number of trades"]
    frame.set_index(frame.columns[0],inplace=True)
    frame=frame.astype(float)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    return frame




def create_TS(df,TS_lenght =10,fee=0.01):
    
    ret = (df["Close"]-df["Open"])/df["Open"]
    ret_high = df["High"].pct_change(1)
    ret_low = df["Low"].pct_change(1)
    
    ret_MA5=ret.rolling(5).mean()
    ret_MA10=ret.rolling(10).mean()
    ret_MA24=ret.rolling(24).mean()
    ret_EWMA= ret.ewm(com=1).mean()
    std_30 = ret.rolling(30).std()
    std_90=ret.rolling(90).std()
    
    ret_high_MA5=ret_high.rolling(5).mean()
    ret_high_MA10=ret_high.rolling(10).mean()
    ret_high_MA24=ret_high.rolling(24).mean()

    
    ret_low_MA5=ret_low.rolling(5).mean()
    ret_low_MA10=ret_low.rolling(10).mean()
    ret_low_MA24=ret_low.rolling(24).mean()

    volume = df["Volume"]
    nb_trade = df["Number of trades"]
    
    all_TS = pd.concat((ret,std_30,std_90,ret_MA5,ret_MA10,ret_MA24,ret_EWMA,ret_high,ret_high_MA5,ret_high_MA10,ret_high_MA24,ret_low,ret_low_MA5,ret_low_MA10,ret_low_MA24,volume,nb_trade),axis=1)
    #all_TS = pd.concat((std_30,std_90,ret,ret_MA5,ret_MA10,ret_high,ret_high_MA5,ret_high_MA10,ret_low,ret_low_MA5,ret_low_MA10,volume,nb_trade),axis=1)
    all_TS.dropna(inplace=True)
    
    all_TS=all_TS.iloc[:-1]
    Y = ret.shift(-1)-fee
    Y = (Y>0).astype(int)
    Y = Y.loc[all_TS.index]
    
    
    TS_numpy=[]
    TS_lenght =10
    Y=Y.iloc[TS_lenght:]
    for i in range(TS_lenght,len(all_TS)):
        data_i = all_TS.iloc[(i-TS_lenght):i,:].values 
        TS_numpy.append(data_i)
        
    return np.array(TS_numpy),Y.index,ret
    
def create_target(ret,price_limit=0.005):
    ret_shift = ret.shift(-1).dropna()
    y=np.zeros(len(ret_shift))
    
    for i in range(len(y)):
        if ret_shift.iloc[i] >= price_limit:
            y[i]=1
         
    y=pd.DataFrame(y,index=ret_shift.index)
    return y

def create_fix_train_test(X,ret,index_data,train_size,validation_size):
    
    Y = create_target(ret)
    Y=Y.loc[index_data]
    Y.sum()/len(Y)
    

    encoder = LabelEncoder()
    encoder.fit(Y)
    encoded_Y = encoder.transform(Y)
    dummy_y = np_utils.to_categorical(encoded_Y)
    
    X_train = X[:int(len(X)*train_size)]
    X_test = X[int(len(X)*train_size):]
    Y_train = dummy_y[:int(len(X)*train_size)]
    Y_test=dummy_y[int(len(X)*train_size):]
    
    X_val = X_train[int(len(X)*(1-validation_size)):]
    Y_val = Y_train[int(len(X)*(1-validation_size)):]
    X_train = X_train[:int(len(X)*(1-validation_size))]
    Y_train = Y_train[:int(len(X)*(1-validation_size))]
    
    ind_train = index_data[:int(len(X)*train_size)]
    ind_test = index_data[int(len(X)*train_size):]
    
    
    
    scalers = {}
    for i in range(X_train.shape[2]):
        scalers[i] = StandardScaler()
        X_train[:, :, i] = scalers[i].fit_transform(X_train[:, :, i]) 
    
    for i in range(X_test.shape[2]):
        X_test[:, :, i] = scalers[i].transform(X_test[:, :, i])
        
    return X_train,X_test,Y_train,Y_test,ind_train,ind_test
