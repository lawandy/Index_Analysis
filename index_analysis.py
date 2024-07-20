#!/usr/bin/env python3

# Load libraries
import pandas as pd
import yfinance as yf
import seaborn as sns
from scipy.stats import norm
import numpy as np
from scipy.stats.mstats import winsorize
import os

# Change directory
os.chdir('/Users/stenson/Desktop')

# Download data
df = yf.download("TNA SPY ^FVX ^RUT", start='2020-01-01', end='2024-04-01')

# Drop variables
#df = df.loc[:,('Adj Close', 'SPY'):('Adj Close', '^FVX')]

# Flatten index
#df.columns = ['_'.join(col) for col in df.columns.values]

# Annualize risk-free rate
#df['rf'] = df['Adj Close_^FVX']/365/100