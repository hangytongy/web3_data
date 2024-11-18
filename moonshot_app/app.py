import requests
import time

def post_message(message):
    
    tele_chatid = ''
    tele_api= ''
    
    payload = {'chat_id' : tele_chatid, 'text' : message, 'parse_mode' : "HTML"}
    response = requests.post(tele_api, json=payload)
    
    if response.status_code == 200:
        print("post sucessful")
    else:
        print(f"error in posting {response}")


def main():
    
    url = 'https://moonshot.umi.cat/api/categories?limit=10'
    count = 0
    tickers_list = []
    
    while True:
        
        try: 
            response = requests.get(url)

            for i in response.json():
                if i['name'] == "New":
                    New = i

            for coin_info in New['coins']:
                ticker = coin_info['ticker']
                if ticker not in tickers_list:
                    tickers_list.append(ticker)
                    print(f'append {ticker} to list')
                    time_listed = coin_info['listedAt']

                    intent = f"Token : {ticker} \nListed Time : {time_listed}"
                    message = u'\U00002744' + " <b>NEW LIStING:</b> \n " + intent
                    post_message(message)

        except Exception as e:
            print(e)
            count += 1
        
        if count > 10:
            break
            
        time.sleep(3)

if __name__ == "__main__":
    main()