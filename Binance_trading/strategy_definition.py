# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 12:18:07 2023

@author: corentin
"""

import pandas as pd
import numpy as np
from simulate_strategy import simulation_strategy



def strategy_random(past_df,position):
    random_nb = np.random.rand()
    
    if position==0:
        if random_nb>0.5:
            new_position=1
        else :
            new_position=position
    else :
       if random_nb>0.5:
           new_position=0
       else :
            new_position=position
           
    return new_position
    
    
test = simulation_strategy()
test.simulate_strat_train(strategy_random)


pnl=test.pnl_train
