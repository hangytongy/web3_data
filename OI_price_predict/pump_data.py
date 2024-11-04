import pandas as pd
import matplotlib.pyplot as plt
from misc_func import get_colors
import os
import numpy as np 
import requests
from datetime import datetime, timedelta


def get_data_funding(ticker,start_time,end_time):

    url = 'https://fapi.binance.com/fapi/v1/fundingRate'

    params = {
        'symbol' : f'{ticker}USDT',
        'startTime' : start_time,
        'endTime' : end_time,
        'limit' : 1000
    }
    
    response = requests.get(url,params = params)
    df = pd.DataFrame(response.json())
    df['time'] = pd.to_datetime(df['fundingTime'], unit = 'ms')
    df['fundingRate'] = df['fundingRate'].astype(float)
    df['markPrice'] = df['markPrice'].astype(float)
    
    return df


def get_pump_data(OI_lim_lower,df_merge,token,start_time,end_time):

    ratio = df_merge['Ratio'].loc[1:].apply(lambda x : abs(x))
    ratio_upper = np.percentile(ratio,95)

    cond_1 = df_merge['open_interest_change_%'] < OI_lim_lower
    cond_2 = df_merge['Ratio'] > ratio_upper
    pump = df_merge[cond_1 & cond_2]

    df_funding = get_data_funding(token,start_time,end_time)

    pump_new = []
    for row_pump in range(len(pump)):
        time = pump['time'].iloc[row_pump]
        lower_time = time - timedelta(hours = 8)
        upper_time = time + timedelta(hours = 8)
        
        for row in range(len(df_funding)):
            if df_funding['time'].iloc[row] >= lower_time and df_funding['time'].iloc[row] <= upper_time and df_funding['fundingRate'].iloc[row] < 0:
                pump_new.append(pump.iloc[row_pump])
    pump_new = pd.DataFrame(pump_new)
    pump_new = pump_new.drop_duplicates()
    return pump_new