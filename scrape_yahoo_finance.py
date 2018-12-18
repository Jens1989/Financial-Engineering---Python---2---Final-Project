# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 08:32:34 2018

@author: BBG841823
"""

import bs4 as bs
import urllib.request
import pandas as pd
import time
import datetime

def get_ticker(ticker, date1, date2, frequency):

    
    if frequency == 'daily':
        interval = '1d'
    elif frequency == 'weekly':
        interval = '1w'
    elif frequency == 'monthly':
        interval = '1mo'
    
    format_string='%Y-%m-%d %H:%M:%S'
 
    # One day (86400 second) adjustment required to get dates printed to match web site manual output
    _date1 = date1.strftime("%Y-%m-%d 00:00:00")
    date1_epoch = str(int(time.mktime(time.strptime(_date1, format_string)))- 86400)
    print("")
    print(date1, date1_epoch, " + 86,400 = ", str(int(date1_epoch) + 86400))
 
    _date2 = date2.strftime("%Y-%m-%d 00:00:00")
    date2_epoch = str(int(time.mktime(time.strptime(_date2, format_string))))
    print(date2, date2_epoch)
 
    url = 'https://finance.yahoo.com/quote/' + ticker + '/history?period1=' + date1_epoch + '&period2=' + date2_epoch + '&interval='+interval+'&filter=history&frequency='+interval
    source = urllib.request.urlopen(url).read()      
    soup =bs.BeautifulSoup(source,'lxml')
    tr = soup.find_all('tr')
      
    data = []
      
    for table in tr:
        td = table.find_all('td')
        row = [i.text for i in td]
        data.append(row)        
      
    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
  
    data = data[1:-2]
    df = pd.DataFrame(data)
    df.columns = columns
    df.set_index(columns[0], inplace=True)
    df = df.convert_objects(convert_numeric=True)
    df = df.iloc[::-1]
    df.dropna(inplace=True)
      
    return df

def scrape(ticker, start_date, end_date, frequency):
    
    today = datetime.date.today()
    # Initialize 'date1'
    date1 = start_date
     
    # Do not allow the 'End Date' to be AFTER today
    if today < end_date:
      end_date = today
     
    iteration_number = 0
    while date1 <= end_date:
        iteration_number += 1
     
        # Create 'date2' in a 60 day Window or less
        date2 = date1 + datetime.timedelta(days=60)
        date2 = datetime.date(date2.year, date2.month, 1)
        date2 = date2 - datetime.timedelta(days=1)
             
        # Do not allow 'date2' to go beyond the 'End Date'
        if date2 > end_date:
            date2 = end_date
             
        print("Processing {} thru {}.".format(date1, date2))
        df = get_ticker(ticker, date1, date2,frequency)
         
        if iteration_number == 1:
            dfall = df.copy()
        else:
            frames = [dfall, df]
            dfall = pd.concat(frames)
     
        date1 = date1   + datetime.timedelta(days=60)
        date1 = datetime.date(date1.year, date1.month, 1)
    
        # Output all 'original' dates
    print(' ')
    print('Today     :', today)
    print(' ')
    print("len of dfall = {}".format(len(dfall)))
    
    return dfall

def date_converter(df):
    
    dates = df.index
    new_dates = []

    for date in dates:
        new_dates.append(datetime.datetime.strptime(date, '%b %d, %Y'))
        
    df.index = new_dates
    df.index.names = ['Date']
    
    return df

def clean_data(df):
    
    df = df.drop(columns='Volume')
    t_list = []
    f_list = []
    dates = []

    df = df.dropna()
    df = df[df['Open'] != '-']
    
    for date, values in df.iterrows():
        
        t_list = []
        
        for value in values:
            
                if value == '-':
                    
                    df.drop(date)
                
                elif ',' in str(value):
                    
                    converted_value = float(value.replace(',',''))
                    t_list.append(converted_value)
                
                else:
                    
                    t_list.append(value)
        
        
        columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        f_list.append(t_list)
        dates.append(date)
        df = pd.DataFrame(f_list, index=dates)
        df.columns = columns
    
    return df

def scrape_data(ticker, start_date, end_date, frequency):
    
    '''
    date1 and date2 are the start and enddates, to be entered as datetime objects
    eg : datetime.date(2015, 6, 19)
    frequency will be daily, weekly or monthly
    '''
    
    df = clean_data(date_converter(scrape(ticker, start_date, end_date, frequency)))

    return df
