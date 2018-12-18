# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 11:19:26 2018

@author: Jens
"""

import datetime
from scrape_yahoo_finance import scrape_data
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pylab
import statsmodels.api as sm

start_date = datetime.date(1993, 4, 19)
end_date = datetime.date(2018, 6, 19)

index_tickers = ['^DJI', '^SP500TR','^IXIC', '^GDAXI', '^HSI']  
index_names = ['Dow Jones', 'SP500', 'NASDAQ', 'DAX', 'HANGSENG']

start =datetime.date(1987, 1, 1)
end = datetime.date(1987, 12, 31)
DJIA = scrape_data('^DJI', start, end, 'daily') 

index_data = {}

for ticker, index_name in zip(index_tickers, index_names):
    
    index_data[index_name] = scrape_data(ticker, start_date, end_date, 'daily')

for ticker in index_data:
    
    index_data[ticker]['Returns'] = index_data[ticker]['Adj Close'].pct_change()
    index_data[ticker] = index_data[ticker].dropna()

def lognormality_test(df, title, alpha = 1e-3): # on adjusted closes
    '''
    test for lognormal distribution.
    the values are turned into log values and then tested
    for normality. 
    '''
    
    logs = []
    
    for num in df['Adj Close']:
        
        logs.append(np.log(num))
        
    statistic, p = stats.normaltest(logs)
    
    if p < alpha: # null hypothesis: normal distribution
        
        print ('p-value: ', p )
        print (' ')
        print("The null hypothesis can be rejected, the distribution is not normal")
        
    else:
        print ('p-value: ', p )
        print (' ')
        print("The null hypothesis cannot be rejected")
        
    plt.hist(logs, bins=100)
    plt.title(title + ': normal distribution of log prices')
    plt.show()
    plt.clf()
    stats.probplot(logs, dist="norm", plot=pylab)
    plt.show()
    plt.clf()
    

def normality_test(df, title, alpha = 1e-3): # on returns
    
    
    returns = df['Adj Close'].pct_change()
    returns = returns.dropna()
    
    statistic, p = stats.normaltest(returns)
    
    if p < alpha: # null hypothesis: normal distribution
        
        print ('p-value: ', p )
        print (' ')
        print("The null hypothesis can be rejected, the distribution is not normal")
        
    else:
        print ('p-value: ', p )
        print (' ')
        print("The null hypothesis cannot be rejected")
    
    plt.hist(returns, bins=100)
    plt.title(title + ': normal distribution of returns')
    plt.show()
    plt.clf()
    stats.probplot(returns, dist="norm", plot=pylab)
    plt.show()
    plt.clf()

def probability_1987_event(DJIA):
    
    annual_vol = 0.2 # given assumption
    daily_vol = annual_vol/np.sqrt(252)
    
    DJIA['Returns'] = DJIA['Adj Close'].pct_change()
    DJIA = DJIA.dropna()
    
    black_monday = round(min(DJIA['Returns']),2)
    
    '''
    I take the assumption that mean is zero
    I calculated the mean returns from 1987 to 2008 which was about 0.03% 
    so I will use zero
    '''
    z_score = black_monday/daily_vol

    prob = stats.norm.sf(abs(z_score))
    
    print ('''
           
           annual volatility: %s
           daily volatility: %s
           black monday return: %s
           z-score: %s
           probability of a black monday event happening: %s'''
           %(annual_vol,round(daily_vol,3),black_monday,round(z_score,2),prob))
    
def fat_tail_sniper(ticker_df):
    
    std = np.std(ticker_df['Returns'])
    
    # filter the df for returns which are higher than 3 standard deviations
    outliers = ticker_df[ticker_df['Returns'] < -3*std] 
    new_index = []
    outliers_index = outliers.index.tolist()
    full_index = ticker_df.index.tolist()
    
    for date in full_index:
        
        if date not in outliers_index:
            new_index.append(date)
    
    df_without_outliers = ticker_df.loc[new_index]
    
    plt.hist(df_without_outliers['Returns'], bins=100)
    plt.hist(outliers['Returns'], color='r')

def plot_tails():

    plt.figure(figsize=(10,10))
    
    for num, ticker in enumerate(index_data):
        
        plt.subplot(2,3,num+1)
        plt.title(list(index_data.keys())[num])
        fat_tail_sniper(index_data[ticker])

def hurst(returns, n):
    
    retn = returns[0:n]
    yn = retn-np.mean(retn)
    zn = np.cumsum(yn)
    Rn = np.max(zn) - min(zn)
    Sn = np.std(retn)
    En = Rn/Sn

    return np.log(En)

def summary(returns):

    y = [hurst(returns, np.size(returns)), hurst(returns,int(np.size(returns)/2)), 
        hurst(returns,int(np.size(returns)/4)), hurst(returns,int(np.size(returns)/8)),
        hurst(returns,int(np.size(returns)/16)), hurst(returns,int(np.size(returns)/32))]
    
    x = [np.log(np.size(returns)), np.log(int(np.size(returns)/2)),
         np.log(int(np.size(returns)/4)), np.log(int(np.size(returns)/8)),
         np.log(int(np.size(returns)/16)), np.log(int(np.size(returns)/32))]
    
    x = sm.add_constant(x)
    model = sm.OLS(y,x)
    results = model.fit()
#    print (results.summary())
    print ('hurst component: ', results.params[1])
    print ('fractal dimension: ', 2-results.params[1])

if __name__ == '__main__':
    
    lognormality_test(index_data['Dow Jones'], title='Dow Jones')
    normality_test(index_data['Dow Jones'], title='Dow Jones')
    print(' ')
    print(' Black Monday')
    probability_1987_event(DJIA)
    plot_tails()
    
    start = datetime.date(2008, 6, 19)
    end = datetime.date(2018, 6, 19)
    
    nasdaq = index_data['NASDAQ'].loc[start:end]
    
    print('''
          
          ''')
    summary(nasdaq['Returns'])
    
    

    
