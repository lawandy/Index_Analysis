#!/usr/bin/env python3

# Load libraries
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import os

'''
Params
'''
# Params
indexes = "TNA SPY TQQQ SPXL ^IRX"

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

def sharpe_ratio(df, varname):
    # Calculate total return for each date
    df['return'] = df[varname]/df[varname].shift(1)-1
    df['return'].iloc[0] = 0

    # Subtract risk free rate
    df['sr'] = df['return'] - df['^IRX']/(100*365)

    # Calculate sharpe ratio
    sr = df['sr'].mean()/df['return'].std()*(252**.5)
    print("Sharpe Ratio is " + str(sr))

    return df

'''
Download Data
'''
# Download data
df_raw = yf.download(indexes, start='2009-01-01')

# Flatten df 
dfs = df_raw.xs('Adj Close', axis=1, level=0, drop_level=True)

'''
Run tools
'''

varname = 'TQQQ'
max_drawdown(dfs[[varname]], varname)
test = sharpe_ratio(dfs, varname)