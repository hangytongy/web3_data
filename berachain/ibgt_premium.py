import requests
import os
import time

def get_ratio():

    chain_id = "berachain"
    pair_ids = [
    "0x1207C619086A52edEf4a4b7Af881B5dDd367a919",  # IBGT
    "0x2c4a603A2aA5596287A06886862dc29d56DbC354",  # BERA
    ]

    prices = {}

    for pair_id in pair_ids:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_id}"
        response = requests.get(url).json()
    
        prices[pair_id] = float(response['pairs'][0]['priceUsd']) if response.get('pairs') else 0

    ibgt, bera = prices[pair_ids[0]], prices[pair_ids[1]]

    print(ibgt)
    print(bera)

    if ibgt != 0 and bera != 0:
        ratio = ibgt/bera
        print(ratio)
        return f"ibgt/bera ratio = {ratio}"

    else:
        return "ibgt, bera return error from api"

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
    message = get_ratio()
    post_message(message)
    
if __name__ == "__main__":
    main()
    time.sleep(60*60*24)
