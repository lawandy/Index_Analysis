#!/usr/bin/env python3

# Load libraries
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import os
from analysis_tools import *

'''
Params
'''
# Params
indexes = "TNA SPY TQQQ SPXL"

# Change directory
os.chdir('/Users/stenson/Desktop')

''' 
Functions
'''
def max_drawdown(df, varname):
    # Calculate total return for each date
    df['return'] = df[varname]/df[varname].shift(1)-1
    df['return'].iloc[0] = 0

    # Calculate the cumulative total return
    df['cum_return'] = (1 + df['return']).cumprod() - 1
                        
    # Create wealth index
    df['wealth_index']=100*(1 + df['cum_return'])

    # Calculate previous peak
    df['prev_peak']=df['wealth_index'].cummax()

    # Calculate max drawdown
    df['max_drawdown']= (df['wealth_index']-df['prev_peak'])/df['prev_peak']

    # Plot 
    plt.plot(df['max_drawdown'])
    plt.xlabel(varname)
    plt.xticks(rotation=90)

    # Return df
    return(df)

'''
Download Data
'''
# Download data
df_raw = yf.download(indexes, start='2009-01-01', end='2024-04-01')

# Flatten df 
df = df_raw.xs('Adj Close', axis=1, level=0, drop_level=True)

'''
Run tools
'''
varname = 'TQQQ'
max_drawdown(df[[varname]], varname)