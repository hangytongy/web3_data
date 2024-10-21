import pandas as pd
import matplotlib.pyplot as plt
from misc_func import get_colors
import os

def get_dump_data(OI_lim,df_merge):

    if OI_lim is not None:
        OI_upper_lim = OI_lim
        cond_1 = df_merge['open_interest_change_%'] > OI_upper_lim
        cond_2 = (df_merge['Ratio'] < 1) & (df_merge['Ratio'] > -0.1)
        dump = df_merge[cond_1 & cond_2]

        return dump 
    else:
        return pd.DataFrame()

def plotting_dump(df_merge,dump,token,data_directory):
#plots on intra interval
    token_chart_directory = os.path.join(data_directory,f"{token}.png")

    colors_ratio,colors_OI = get_colors(dump)

    fig, (ax1,ax2) = plt.subplots(nrows=2, ncols = 1, figsize=(20, 14))

    #plot 1

    ax1.plot(df_merge['time'], df_merge['Close'], color='b', label='Close Price', linewidth = 3)
    ax1.set_title(f'Price History {token}', fontsize = 16)
    ax1.set_xlabel('Date', fontsize = 14)
    ax1.set_ylabel('Price in USDT', color='b', fontsize = 14)
    ax1.tick_params(axis='y', labelcolor='b', labelsize = 14)

    ax1_twin = ax1.twinx()
    ax1_twin.bar(dump['time'], dump['open_interest_change_%'], color = 'red', label = 'IO change %', width = 0.02)
    ax1_twin.set_ylabel('% change', fontsize = 14)
    ax1_twin.set_ylabel('Open interest % change', color='r', fontsize = 14)
    ax1_twin.tick_params(axis='y', labelcolor='r', labelsize = 14)

    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='lower right')

    #plot 2

    ax2.plot(df_merge['time'], df_merge['Close'], color='b', label='Close Price',linewidth = 3)
    ax2.set_title(f'Price History {token}', fontsize = 16)
    ax2.set_xlabel('Date', fontsize = 14)
    ax2.set_ylabel('Price in USDT', color='b', fontsize = 14)
    ax2.tick_params(axis='y', labelcolor='b', labelsize = 14)

    ax2_twin = ax2.twinx()
    ax2_twin.bar(dump['time'], dump['Ratio'],  color = 'red', label='Price % Change vs IO Change', width = 0.02)
    ax2_twin.set_xlabel('Date', fontsize = 14)
    ax2_twin.set_ylabel('Delta price to IO', color='r', fontsize = 14)
    ax2_twin.tick_params(axis='y', labelcolor='r', labelsize = 14)
    #ax2_twin.set_ylim(-100,100)

    ax2.legend(loc='best')
    ax2_twin.legend(loc='best')

    plt.xticks(rotation=45)
    ax1.grid()
    ax2.grid()
    plt.tight_layout()

    fig.savefig(token_chart_directory)
    return token_chart_directory