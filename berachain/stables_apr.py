import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

def get_apr():

    infrared = "https://infrared.finance/api/vault/beraswap-usdc.e-honey?chainId=80094"
    response = requests.get(infrared)
    infrared_stables_apr = round(response.json()['reward_tokens'][0]['apr']*100,2)
    
    dolomite = "https://api.dolomite.io/tokens/80094/interest-rates"
    response = requests.get(dolomite)    
    dolomite_usdc = {}
    dolomite_honey = {}
    for token in response.json()['interestRates']:
        if token['token']['tokenSymbol'] == "USDC":
            print(token['token']['tokenSymbol'])
            print(round(float(token['supplyInterestRate'])*100,2))
            print(round(float(token['borrowInterestRate'])*100,2))
            dolomite_usdc['supply'] = round(float(token['supplyInterestRate'])*100,2)
            dolomite_usdc['borrow'] = round(float(token['borrowInterestRate'])*100,2)
        elif token['token']['tokenSymbol'] == "HONEY":
            print(token['token']['tokenSymbol'])
            print(round(float(token['supplyInterestRate'])*100,2))
            print(round(float(token['borrowInterestRate'])*100,2))
            dolomite_honey['supply'] = round(float(token['supplyInterestRate'])*100,2)
            dolomite_honey['borrow'] = round(float(token['borrowInterestRate'])*100,2)

    message = f"BERACHAIN APR comparison: \n\nInfrared HONEY/USDC APR : {infrared_stables_apr}% \nDolomite USDC supply APR : {dolomite_usdc['supply']}% \nDolomite USDC borrow APR : {dolomite_usdc['borrow']}% \nDolomite Honey supply APR : {dolomite_honey['supply']}% \nDolomite Honey borrow APR : {dolomite_honey['borrow']}%"
    
    return message

def post_message(message):
    
    tele_chatid = ''
    thread_id = ''
    tele_api= ''
    url = f"https://api.telegram.org/bot{tele_api}/sendMessage"
    
    payload = {'chat_id' : tele_chatid, "message_thread_id": thread_id,'text' : message, 'parse_mode' : "HTML"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("post sucessful")
    else:
        print(f"error in posting {response}")
        
def main():
    message = get_apr()
    post_message(message)
    
if __name__ == "__main__":
    main()
    time.sleep(60*60*24)
