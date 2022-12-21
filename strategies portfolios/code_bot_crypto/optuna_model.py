# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:32:24 2022

@author: corentin
"""
import numpy as np
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Conv2D,GRU,Concatenate,MaxPooling2D,MaxPooling1D,Flatten
import optuna
from keras.optimizers import Adam
from numpy.random import seed
import tensorflow
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils


class trading_bot :
    
    def __init__(self,X,ret,index_data,train_size,validation_size,fee=0.001):
        
        self.X=X
        self.ret=ret
        self.index_data=index_data
        self.fee = fee
        self.create_fix_train_test(train_size,validation_size)
        
        
    def create_target(self,price_limit=0.005):
        ret_shift = self.ret.shift(-1).dropna()
        
        y=np.zeros(len(ret_shift))
        
        for i in range(len(y)):
            if ret_shift.iloc[i] >= price_limit:
                y[i]=1
             
        y=pd.DataFrame(y,index=ret_shift.index)
        return y
        
    def create_fix_train_test(self,train_size,validation_size):
        
        Y = self.create_target()
        Y=Y.loc[self.index_data]
        Y.sum()/len(Y)

        encoder = LabelEncoder()
        encoder.fit(Y.iloc[:,0])
        encoded_Y = encoder.transform(Y.iloc[:,0])
        dummy_y = np_utils.to_categorical(encoded_Y)
        
        X_train = self.X[:int(len(self.X)*train_size)]
        X_test = self.X[int(len(self.X)*train_size):]
        Y_train = dummy_y[:int(len(self.X)*train_size)]
        Y_test=dummy_y[int(len(self.X)*train_size):]
        
        
        
        ind_train = self.index_data[:int(len(self.X)*train_size)]
        ind_test = self.index_data[int(len(self.X)*train_size):]
        
        ind_val = ind_train[int(len(X_train)*(1-validation_size)):]
        ind_train = ind_train[:int(len(X_train)*(1-validation_size))]
        X_val = X_train[int(len(X_train)*(1-validation_size)):]
        Y_val = Y_train[int(len(X_train)*(1-validation_size)):]
        
        Y_train = Y_train[:int(len(X_train)*(1-validation_size))]
        X_train = X_train[:int(len(X_train)*(1-validation_size))]
        
        scalers = {}
        for i in range(X_train.shape[2]):
            scalers[i] = StandardScaler()
            X_train[:, :, i] = scalers[i].fit_transform(X_train[:, :, i]) 
        for i in range(X_test.shape[2]):
            X_test[:, :, i] = scalers[i].transform(X_test[:, :, i])
            X_val[:, :, i] = scalers[i].transform(X_val[:, :, i])
        
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.Y_train = Y_train
        self.Y_val = Y_val
        self.Y_test = Y_test
        self.ind_train = ind_train
        self.ind_val = ind_val
        self.ind_test = ind_test

    def get_pred_val(self,y_pred):
        val=1
        ret_y = self.ret.shift(-1)
        strat_values = []
        for ind in y_pred.index:
            if y_pred.loc[ind].values==1:
                val*=(1+ret_y.loc[ind]-2*self.fee)
    
            strat_values.append(val)
        strat_values=pd.DataFrame(strat_values,index=y_pred.index)
        return strat_values

    def build_model(self,params):
        
        optimizer = Adam(params['learning_rate'])
        model = Sequential()
        model.add(GRU(params['n_RNN'],input_shape=(self.X.shape[1],self.X.shape[2]),return_sequences=True))
        model.add(MaxPooling1D(pool_size=2,padding='valid'))
        model.add(Flatten())
        model.add(Dense(params['n_Dense1'], activation = params['activation_Dense1']))
    
        
        model.add(Dense(params['n_Dense2'], activation = params['activation_Dense2']))
        
        model.add(Dense(2, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    
        #model_lstm.summary()
        return model



    def find_good_model(self,n_trial):
        
        def objective(trial,verbose=False):
            
            tensorflow.random.set_seed(42)
            seed(42)
            
            
            params = {
                'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-1),
                'n_RNN': trial.suggest_int("n_RNN", 5, 30),
                'n_Dense1': trial.suggest_int("n_Dense1", 5, 25),
                'n_Dense2': trial.suggest_int("n_Dense2", 5, 25),
                
                'activation_Dense1': trial.suggest_categorical("activation_Dense1", ["tanh", "relu","selu"]),
                'activation_Dense2': trial.suggest_categorical("activation_Dense2", ["tanh", "relu","selu"]),
                'epochs' : trial.suggest_int("epochs", 30, 100),
                'batch_size' : trial.suggest_int("batch_size", 2, 30)
                }
            
            model = self.build_model(params)
            model.fit(
                self.X_train,
                self.Y_train,
                epochs = params['epochs'],
                batch_size = params['batch_size'],
                verbose=False
            )
    
            Y_pred = model.predict(self.X_val)
            Y_pred=np.argmax(Y_pred,axis=1)
            Y_pred=pd.DataFrame(Y_pred,index=self.ind_val)
            strat_val = self.get_pred_val(Y_pred)
            ret_start = strat_val.pct_change(1).iloc[:,0]
            ret_mean=ret_start.mean()*365
            
            if verbose :
                print(params)
                print("return : ",ret_start.mean()*365)
            
            return ret_mean
        
        
        
        self.study = optuna.create_study(direction="maximize")
        
        
        self.study.optimize(lambda trial: objective(trial), n_trials=n_trial)
        #study.optimize(lambda trial: objective(trial, X_train,X_test,Y_train,Y_test,ind_test,ret,verbose=True), n_trials=1)
        
    
        trial = self.study.best_trial
        
        self.best_param = {
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-6, 1e-2),
            'n_RNN': trial.suggest_int("n_RNN", 5, 40),
            'n_Dense1': trial.suggest_int("n_Dense1", 5, 40),
            'n_Dense2': trial.suggest_int("n_Dense2", 5, 40),
            'activation_Dense1': trial.suggest_categorical("activation_Dense1", ["tanh", "relu","selu"]),
            'activation_Dense2': trial.suggest_categorical("activation_Dense2", ["tanh", "relu","selu"]),
            'epochs' : trial.suggest_int("epochs", 30, 100),
            'batch_size' : trial.suggest_int("batch_size", 2, 30)
            }
        
        best_model = self.build_model(self.best_param)
        best_model.fit(
            self.X_train,
            self.Y_train,
            epochs = self.best_param['epochs'],
            batch_size = self.best_param['batch_size'],
            verbose=False
        )
    
        Y_pred = best_model.predict(self.X_test)
        Y_pred=np.argmax(Y_pred,axis=1)
        Y_pred=pd.DataFrame(Y_pred,index=self.ind_test)
        strat_val = self.get_pred_val(Y_pred)
        ret_start = strat_val.pct_change(1).iloc[:,0]
        print("return : ",ret_start.mean()*365)
        print("std : ",ret_start.std()*np.sqrt(365))
        print("sharpe : ",ret_start.mean()*np.sqrt(365)/ret_start.std())
        
        full_strat = (1+self.ret.loc[strat_val.index]).cumprod()
        #full_strat.plot()
    
        self.strategies = pd.concat((strat_val,full_strat),axis=1)
        self.strategies.columns=["NN_strat","crypto"]
        self.strategies.plot()
        
        
    
    
    
    
    


