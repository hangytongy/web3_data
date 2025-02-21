from datetime import datetime, timedelta
import time
import requests



def get_positions(user):
    print("get pos")
    url = "https://api.hyperliquid.xyz/info"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {"type": "clearinghouseState",
             'user' : user}
    
    response = requests.post(url,headers=headers, json=data)
    
    return response.json()

def get_message(user):
    print("get txs")
    url = "https://rpc.hyperliquid.xyz/explorer"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "type": "userDetails",
        "user": user
    }

    response = requests.post(url, headers=headers, json=data)
    
    now = datetime.now()
    five_min = now - timedelta(minutes=5)
    five_min = int(five_min.timestamp()*1000)
    needed_tx = []
        
    for txs in response.json()['txs'][:10]:
        if txs['time'] > five_min and txs['action']['type'] == 'order':
            tx = f"https://app.hyperliquid.xyz/explorer/tx/{txs['hash']}"
            needed_tx.append(tx)
    if needed_tx:
        return f'tansactions in past 5 min : {" ".join(needed_tx)}'


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
    
user = ""
while True:
    message = get_message(user)
    if message:
        pos = get_positions(user)
        total_message = f"{message} \n{pos}"
        print(total_message)
        post_message(total_message)
        
    print("sleep....5min")
    time.sleep(60*5)
