# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:53:33 2022

@author: corentin
"""
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold,TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from datetime import datetime
import matplotlib.pyplot as  plt
import sklearn
from binance import Client
client=Client()

def getdailydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,"8h","3 years ago UTC"))
    frame=frame[[0,1,2,3,4,5,8]]
    frame.columns=["Timestamp","Open","High","Low","Close","Volume","Number of trades"]
    frame.set_index(frame.columns[0],inplace=True)
    frame=frame.astype(float)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    return frame




def create_TS(df):
    
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
    Y = ret.shift(-1)-0.01
    Y = (Y>0).astype(int)
    Y = Y.loc[all_TS.index]
    
    
    TS_numpy=[]
    TS_lenght =25
    Y=Y.iloc[TS_lenght:]
    for i in range(TS_lenght,len(all_TS)):
        data_i = all_TS.iloc[(i-TS_lenght):i,:].values 
        TS_numpy.append(data_i)
        
    return np.array(TS_numpy),Y.index,ret
    
def create_target(ret):
    ret_shift = ret.shift(-1).dropna()
    y=np.zeros(len(ret_shift))
    
    for i in range(len(y)):
        if ret_shift.iloc[i] > 0.002 and ret_shift.iloc[i] < 0.01:
            y[i]=0
        elif ret_shift.iloc[i] >= 0.005:
            y[i]=1
         
    y=pd.DataFrame(y,index=ret_shift.index)
    return y
    



data_source_ETH=getdailydata("ETHUSDT")
X3,index_data,ret=create_TS(data_source_ETH)

data_source_BTC=getdailydata("BTCUSDT")
X1,_,_=create_TS(data_source_BTC)

data_source_XRP=getdailydata("ADAUSDT")
X2,_,_=create_TS(data_source_XRP)

#X = np.concatenate((X3,X1,X2),axis=2)
X=X3

Y = create_target(ret)
Y=Y.loc[index_data]
Y.sum()/len(Y)

from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)
dummy_y = np_utils.to_categorical(encoded_Y)

X_train = X[:int(len(X)*0.9)]
X_test = X[int(len(X)*0.9):]
Y_train = dummy_y[:int(len(X)*0.9)]
Y_test=dummy_y[int(len(X)*0.9):]

ind_train = index_data[:int(len(X)*0.9)]
ind_test = index_data[int(len(X)*0.9):]

from sklearn.preprocessing import StandardScaler

scalers = {}
for i in range(X_train.shape[2]):
    scalers[i] = StandardScaler()
    X_train[:, :, i] = scalers[i].fit_transform(X_train[:, :, i]) 

for i in range(X_test.shape[2]):
    X_test[:, :, i] = scalers[i].transform(X_test[:, :, i])


from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Conv2D,GRU,Concatenate,MaxPooling2D,MaxPooling1D,Flatten
#pip install -U numpy==1.18.5

from numpy.random import seed
import tensorflow
tensorflow.random.set_seed(42)
seed(42)

model_lstm = Sequential()
model_lstm.add(LSTM(10,input_shape=(X.shape[1],X.shape[2]),return_sequences=True))
model_lstm.add(MaxPooling1D(pool_size=2,padding='valid'))
model_lstm.add(Flatten())
model_lstm.add(Dense(8, activation = 'relu'))

#model_lstm.add(Dense(10, activation = 'relu'))
model_lstm.add(Dense(5, activation = 'relu'))
#model_lstm.add(Dropout(0.3))
model_lstm.add(Dense(2, activation='softmax'))
model_lstm.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model_lstm.summary()

model_lstm.fit(
    X_train,
    Y_train,
    validation_split = 0.1,
    epochs = 50,
    batch_size = 12
)

_, accuracy = model_lstm.evaluate(X_train,Y_train)
print('Accuracy train : %.2f' % (accuracy*100))
_, accuracy = model_lstm.evaluate(X_test,Y_test)
print('Accuracy test : %.2f' % (accuracy*100))

Y_pred = model_lstm.predict(X_test)
Y_pred=np.argmax(Y_pred,axis=1)
Y_pred=pd.DataFrame(Y_pred,index=ind_test)




def get_pred_val(y_pred,ret):
    val=1
    ret_y = ret.shift(-1)
    strat_values = []
    for ind in y_pred.index:
        if y_pred.loc[ind].values==1:
            val*=(1+ret_y.loc[ind]-0.002)
        #if y_pred.loc[ind].values==1:
        #    val*=(1+ret_y.loc[ind]-0.002)*0.5
        strat_values.append(val)
    strat_values=pd.DataFrame(strat_values,index=y_pred.index)
    return strat_values

strat_val = get_pred_val(Y_pred,ret)
strat_val.iloc[-1].values

#strat_val.plot()
full_strat = (1+ret.loc[strat_val.index]).cumprod()
#full_strat.plot()

strategies = pd.concat((strat_val,full_strat),axis=1)
strategies.columns=["NN_strat","crypto"]
strategies.plot()

ret_start = strat_val.pct_change(1).iloc[:,0]
print("return : ",ret_start.mean()*365)
print("std : ",ret_start.std()*np.sqrt(365))
print("sharpe : ",ret_start.mean()*np.sqrt(365)/ret_start.std())


ret_start = full_strat.pct_change(1)
print("return : ",ret_start.mean()*365)
print("std : ",ret_start.std()*np.sqrt(365))
print("sharpe : ",ret_start.mean()*np.sqrt(365)/ret_start.std())