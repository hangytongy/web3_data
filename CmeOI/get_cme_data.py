import requests
import pandas as pd


def query_data(token):
    url = f'https://velo.xyz/api/m/cmeOi?product={token}&range=2592000000&resolution=1%20day'
    response = requests.get(url)
    data = response.json()['d']
    data_dict = {'timestamp' : [row[0] for row in data], 'value' : [row[1] for row in data]}
    df = pd.DataFrame(data_dict)
    df['time'] = pd.to_datetime(df['timestamp'], unit = 's')
    df['difference'] = df['value'].diff()
    df.loc[0,'difference'] = 0
    df['difference'] = df['difference'].astype('int64')
    df['difference'] = df['difference'].apply(lambda x: f"{x:,}")

    return df