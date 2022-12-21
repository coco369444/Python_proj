# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 20:28:53 2022

@author: corentin
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as  plt
import sklearn
from binance import Client
client=Client()


def getdailydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,"12h","5 years ago UTC"))
    frame=frame[[0,1,2,3,4,5,8]]
    frame.columns=["Timestamp","Open","High","Low","Close","Volume","Number of trades"]
    frame.set_index(frame.columns[0],inplace=True)
    frame=frame.astype(float)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    return frame

def feature_ret(ret,name):
    std_30 = ret.rolling(30).std()
    std_90=ret.rolling(90).std()
    ret_MA5=ret.rolling(5).mean()
    ret_MA10=ret.rolling(10).mean()
    ret_MA24=ret.rolling(24).mean()
    ret_EWMA= ret.ewm(com=1).mean()
    ret_1=ret.shift(1)
    ret_2=ret.shift(2)
    ret_5=ret.shift(5)
    exit_data= pd.concat((ret,ret_1,ret_2,ret_5,std_30,std_90,ret_MA5,ret_MA10,ret_MA24,ret_EWMA),axis=1)
    exit_data.columns=[name+"ret_1",name+"ret_2",name+"ret_3",name+"ret_5",name+"std_30",name+"std_90",name+"MA_5",name+"MA_10",name+"MA_24",name+"EWMA"]
    
    return exit_data

def preposessing_data(df):
    ret = (df["Close"]-df["Open"])/df["Open"]
    ret_high = df["High"].pct_change(1)
    ret_low = df["Low"].pct_change(1)
    
    ret_feat = feature_ret(ret,"open_close")
    ret_high_feat = feature_ret(ret_high,"high")
    ret_low_feat = feature_ret(ret_low,"low")
    
    
    X = pd.concat((ret_feat,ret_high_feat,ret_low_feat,df["Volume"],df["Number of trades"]),axis=1)
    X["High-Low"]=df["High"]-df["Low"]
    X.dropna(inplace=True)
    X=X.iloc[:-1]
    Y = ret.shift(-1)-0.002
    Y = (Y>0).astype(int)
    Y = Y.loc[X.index]
    
    
    return X,Y,ret
data_source_ETH=getdailydata("ETHUSDT")
X,Y,ret=preposessing_data(data_source_ETH)
    
Y.sum()/len(Y)
from sklearn import preprocessing

X_train = X.iloc[:int(len(X)*0.85)]
scaler = preprocessing.StandardScaler().fit(X_train)
X_train = pd.DataFrame(scaler.transform(X_train),index=X_train.index,columns=X_train.columns)

X_test = X.iloc[int(len(X)*0.85):]
X_test = pd.DataFrame(scaler.transform(X_test),index=X_test.index,columns=X_test.columns)
Y_train = Y.loc[X_train.index]
Y_test=Y.loc[X_test.index]
    
"""
Random Forest
"""
    
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

rf = RandomForestClassifier(n_estimators=500,n_jobs=4)
rf.fit(X_train,Y_train)
Y_pred = rf.predict(X_test)

Y_pred = pd.DataFrame(Y_pred,index=X_test.index)

confusion_matrix(Y_test, Y_pred)

def get_pred_val(y_pred,ret):
    val=1
    ret_y = ret.shift(-1)
    strat_values = []
    for ind in y_pred.index:
        if y_pred.loc[ind].values==1:
            val*=(1+ret_y.loc[ind])
        strat_values.append(val)
    strat_values=pd.DataFrame(strat_values,index=y_pred.index)
    return strat_values

strat_val = get_pred_val(Y_pred,ret)
strat_val.iloc[-1].values

strat_val.plot()

"""
light GBM
"""

from lightgbm import LGBMClassifier
lgb = LGBMClassifier(n_estimators=1000,learning_rate=0.1)
lgb.fit(X_train,Y_train)
Y_pred = lgb.predict(X_test)
Y_pred=pd.DataFrame(Y_pred,index=X_test.index)

confusion_matrix(Y_test, Y_pred)

def get_pred_val(y_pred,ret):
    val=1
    ret_y = ret.shift(-2)
    strat_values = []
    for ind in y_pred.index:
        if y_pred.loc[ind].values==1:
            val*=(1+ret_y.loc[ind])
        strat_values.append(val)
    strat_values=pd.DataFrame(strat_values,index=y_pred.index)
    return strat_values

strat_val = get_pred_val(Y_pred,ret)
strat_val.iloc[-1].values

strat_val.plot()

"""
NN Keras
"""

from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold,TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix


from numpy.random import seed

from tensorflow import set_random_seed
set_random_seed(42)
seed(42)
encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)
# larger model
def create_model():
    model = Sequential()
    
    model.add(Dense(30,input_dim=33, activation='relu'))
    
    model.add(Dense(20, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
	# Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model
#estimators = []
#estimators.append(('standardize', StandardScaler()))
#estimators.append(('mlp', KerasClassifier(build_fn=create_larger, epochs=100, batch_size=5, verbose=1)))
#pipeline = Pipeline(estimators)
#kfold = TimeSeriesSplit(n_splits=2)
#results = cross_val_score(pipeline, X, encoded_Y, cv=kfold,n_jobs=-1)
#print("Larger: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

model_CNN_classique = create_model()
model_CNN_classique.fit(X_train,Y_train, epochs=150, batch_size=4)

_, accuracy = model_CNN_classique.evaluate(X_train,Y_train)
print('Accuracy train : %.2f' % (accuracy*100))
_, accuracy = model_CNN_classique.evaluate(X_test,Y_test)
print('Accuracy test : %.2f' % (accuracy*100))

Y_pred = (model_CNN_classique.predict(X_test) > 0.5).astype(int)
Y_pred=pd.DataFrame(Y_pred,index=X_test.index)
confusion_matrix(Y_test, Y_pred)

def get_pred_val(y_pred,ret):
    val=1
    ret_y = ret.shift(-1)
    strat_values = []
    for ind in y_pred.index:
        if y_pred.loc[ind].values==1:
            val*=(1+ret_y.loc[ind]-0.002)
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

ret_start = strat_val.pct_change(1)
print("return : ",ret_start.mean().values[0]*365)
print("std : ",ret_start.std().values[0]*np.sqrt(365))
print("sharpe : ",ret_start.mean().values[0]*np.sqrt(365)/ret_start.std().values[0])




