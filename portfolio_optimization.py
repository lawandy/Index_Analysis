#!/usr/bin/env python3

# Load libraries
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

''' Functions '''
def sharpe_ratio(df):
    
    varname = "value"

    # Calculate total return for each date
    df['return'] = df[varname]/df[varname].shift(1)-1
    df['return'].iloc[0] = 0

    # Subtract risk free rate
    df['sr'] = df['return'] - df['^IRX']/(100*365)

    # Calculate sharpe ratio
    mean = df['sr'].mean()
    amean = (1 + mean)** 252 - 1
    std = df['return'].std()
    astd = std *(252**.5)
    sr = mean/std*(252**.5)

    # CAGR
    days = (df.index.values[-1]-df.index.values[0]).astype('timedelta64[D]')// np.timedelta64(1, 'D')
    cagr = (df['value'].iloc[-1]/df['value'].iloc[0])**(1/(days/365)) - 1
    
    return pd.DataFrame({'mean': [amean], 'std': [astd], 'sr':[sr], 'cagr': [cagr]})

# Construct portfolio weights
def construct_pw (indexes, pw):

    # Split the indexes string into a list
    index_list = indexes.split()

    # Create the dictionary by zipping the lists together
    return dict(zip(index_list, pw))

# Construct portfolio
def construct_portfolio(df, wt, rebalanceperiod):
    
    # Drop missing rows
    df = df.dropna(thresh=len(df.columns))

    # Initialize
    for stock, weight in wt.items():
        df['sh_' + stock] = 0
        df['value_' + stock] = 0

    # Calculate rebalance
    df['value'] = 100
    for i in range(len(df)):
        
        for stock, weight in wt.items():

            # Calculate new shares
            if i == 0:
                newvalue = wt[stock] * df['value'].iloc[i] / df[stock].iloc[i]
            elif i % rebalanceperiod != 0:
                newvalue = df['sh_' + stock].iloc[i-1]
            elif i % rebalanceperiod == 0:
                newvalue = df['value'].iloc[i-1] * wt[stock] / df[stock].iloc[i]
            df.iloc[i, df.columns.get_loc('sh_' + stock)] = newvalue

            # Calculate new value of stock
            df.iloc[i, df.columns.get_loc('value_' + stock)] = df['sh_' + stock].iloc[i] * df[stock].iloc[i]
        
        ## Get value of portfolio
        # Identify the columns that start with 'value_'
        value_columns = [col for col in df.columns if col.startswith('value_')]

        # Sum the identified columns row-wise and store it in a new column
        df['value'] = df[value_columns].sum(axis=1)

    return df

# Construct rolling sum for bond yields
def convert_yield_to_rs (df, var):
    df[var] = df[var] / 100
    df[var + "_cs"] = 1
    for i in range(1, len(df)-1):
        days = (df.index.values[i+1]-df.index.values[i]).astype('timedelta64[D]')// np.timedelta64(1, 'D')
        df.iloc[i, df.columns.get_loc(var + "_cs")] = df[var + "_cs"].iloc[i-1] * (1+df['^IRX'].iloc[i]/365)**days
    return df

''' Run Program '''

# Params
indexes = "SPY TQQQ ^IRX"
rebalanceperiod = 90

# Change directory
os.chdir('/Users/stenson/Desktop')

# Download data
df_raw = yf.download(indexes, start='2010-02-09')

# Flatten df 
dfs = df_raw.xs('Adj Close', axis=1, level=0, drop_level=True)

# Fill NA
dfs = dfs.fillna(method='ffill')

# Create IRX rolling sum
dfs = convert_yield_to_rs(dfs, "^IRX")

# Test case
# dfs = dfs.iloc[-10:]

# Create weights list
indexes_list = [i for i in indexes.split(' ')]
for index in indexes_list:
    if index == indexes_list[0]:
        wts = pd.DataFrame(np.arange(0.0, 1.0, 0.05), columns=[index])
    else:
        wts = wts.merge(pd.DataFrame(np.arange(0.0, 1.0, 0.05), columns=[index]), how = 'cross')

# Drop if weights don't sum to 1
wts = wts[wts.sum(axis=1, numeric_only=True) == 1]

# Create stats to hold results
stats = []

# Iterate through weights
for i in range(len(wts)):

    # Create weight
    wt = wts.iloc[i].to_dict()
    # wt = {'SPY': 0.45, 'TQQQ': 0.45, '^IRX_cs': 0.1}

    # Construct portfolio
    df = construct_portfolio(dfs, wt, rebalanceperiod)

    # Return stats
    stats.append(pd.DataFrame([wt]).merge(sharpe_ratio(df), how = "cross"))

# Merge stats into dataframe
stats = pd.concat(stats)

# Next steps
# (1) Reconstruct TQQQ index for further backtest
# (2) Rebalance only at lows
