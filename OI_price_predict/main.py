from get_oi_data import init_client, open_interest, get_exchanges, get_price_history
import post_telegram

import pandas as pd
import numpy as np 
import dump_data
import os
from datetime import datetime, timedelta

def run_main(days,token,interval):
    current_datetime = datetime.now()

    #parameters
    client = init_client()
    days = days
    hours = 24 * days
    hour_in_ms = 1000 * 60 * 60 *hours
    start_time = client.timestamp() - hour_in_ms
    end_time = client.timestamp()
    token = token
    interval = interval

    df = open_interest(client,start_time,end_time,token,interval)
    try:
        df = df.reset_index()
        df['time'] = pd.to_datetime(df['time'], unit = 'ms')
        df['open_interest_change'] = df['coin_open_interest_close'].diff()
        df['open_interest_change_%'] =  (df['open_interest_change']/df['coin_open_interest_close'])*100
        df_price = get_price_history(token,interval,end_time,start_time)
        df_price['time'] = pd.to_datetime(df_price.index, unit = 'ms')
        df_merge = df_price.merge(df)
        df_merge['price change'] = df_merge['Close'].diff()
        df_merge['price change %'] = (df_merge['price change']/df_merge['Close'])*100
        df_merge['Ratio'] = df_merge['price change %']/df_merge['open_interest_change_%']
        df_merge = df_merge[['time','Close','coin_open_interest_close','open_interest_change_%','price change %','Ratio']]

        OI = df_merge['open_interest_change_%'].apply(lambda x : abs(x))
        if OI.size > 0:
            OI_lim = np.percentile(OI,95)
            OI_lim_lower = np.percentile(OI,5)
        else:
            print("OI empty")
            OI_lim = None 
            OI_lim_lower = None 

        dump = dump_data.get_dump_data(OI_lim,df_merge)

        directory = os.getcwd()
        data_directory = os.path.join(directory,'data')
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        token_path = os.path.join(data_directory,f'{token}.csv')

        if not dump.empty:
            dump.to_csv(token_path, index=False)

            dump_last_row_time = dump.iloc[-1]['time']
            onehour_before_current = current_datetime - timedelta(hours=1)

            if dump_last_row_time > onehour_before_current:
                print(dump.iloc[-1])
                token_chart_directory = dump_data.plotting_dump(df_merge, dump, token, data_directory)
                post_telegram.send_photo_telegram(token_chart_directory, f"{token} possible DUMP /n{dump.iloc[-1]}")
    except Exception as e:
        print(e)



