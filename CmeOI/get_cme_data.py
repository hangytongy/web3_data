import requests
import pandas as pd


def query_data(token):
    url = f'https://velo.xyz/api/m/cmeOi?product={token}&range=2592000000&resolution=1%20day'
    response = requests.get(url)
    data = response.json()['d']
    data_dict = {'timestamp' : [row[0] for row in data], 'value' : [row[1] for row in data]}
    df = pd.DataFrame(data_dict)
    df['time'] = pd.to_datetime(df['timestamp'], unit = 's')
    df['difference_Dollar'] = df['value'].diff()
    df.loc[0,'difference_Dollar'] = 0
    df['difference_Dollar'] = df['difference_Dollar'].astype('int64')
    df['difference_Dollar'] = df['difference_Dollar'].apply(lambda x: f"{x:,}")

    df = df.iloc[1:].reset_index(drop=True)

    return df

def query_data_coin(token):
    url = f'https://velo.xyz/api/m/cmeOiCoins?product={token}&range=2592000000&resolution=1%20day'
    response = requests.get(url)
    data = response.json()['d']
    data_dict = {'timestamp' : [row[0] for row in data], 'value' : [row[1] for row in data]}
    df = pd.DataFrame(data_dict)
    df['time'] = pd.to_datetime(df['timestamp'], unit = 's')
    df['value'] = df['value'].astype(float)
    df['difference_Coin'] = df['value'].diff()
    df.loc[0,'difference_Coin'] = 0
    df['difference_Coin'] = df['difference_Coin'].astype('int64')
    df['difference_Coin'] = df['difference_Coin'].apply(lambda x: f"{x:,}")

    df = df.iloc[1:].reset_index(drop=True)

    return df

def combine_df(df_dollar,df_coin):
    df_dollar['difference_Coin'] = df_coin['difference_Coin']

    return df_dollar

def cme_data(token):
    df_dollar = query_data(token)
    df_coin = query_data_coin(token)
    df_final = combine_df(df_dollar,df_coin)

    df_final['value'] = df_final['value'].astype(int)
    df_final['time'] = df_final['time'].dt.date

    return df_final