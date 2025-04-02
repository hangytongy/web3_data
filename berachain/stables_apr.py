import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

def get_apr():

    names = ['bex-byusd-honey', 'kodiak-rusd-honey', 'kodiak-wbera-ibgt', 'bex-wbera-ibera']
    infrared = "https://infrared.finance/api/vaults?chainId=80094&show_paused=true&sort_column=tvl"
    
    response = requests.get(infrared)
    data = response.json().get('vaults', [])
    
    # Dictionary to store results dynamically
    infrared_aprs = {name: None for name in names}
    
    for vault in data:
        if vault['id'] in infrared_aprs:
            infrared_aprs[vault['id']] = round(vault['apr'] * 100, 2)
    
    # Assign values to variables if needed
    infrared_stables_apr = infrared_aprs[names[0]]
    infrared_rusd = infrared_aprs[names[1]]
    infrared_ibgt = infrared_aprs[names[2]]
    infrared_ibera = infrared_aprs[names[3]]

    
    url = "https://infrared.finance/api/vault/infrared-ibgt?chainId=80094"
    response = requests.get(url)
    ibgt_apr = 0
    for token in response.json()['reward_tokens']:
        if token['name'] != 'iBGT':
            ibgt_apr += round(token['apr']*100,2) 

    
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

    message = f"BERACHAIN APR comparison: \n\nInfrared HONEY/USDC APR : {infrared_stables_apr}% \nDolomite USDC supply APR : {dolomite_usdc['supply']}% \nDolomite USDC borrow APR : {dolomite_usdc['borrow']}% \nDolomite Honey supply APR : {dolomite_honey['supply']}% \nDolomite Honey borrow APR : {dolomite_honey['borrow']}% \nBera-iBera apr : {infrared_ibera}% \nBera-iBGT apr : {infrared_ibgt}% \nrUSD apr : {infrared_rusd}% \niBGT apr : {ibgt_apr}%"
    
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
    while True:
        main()
        time.sleep(60*60*6)
