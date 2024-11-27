import requests

def get_data(params):
    
    tokens = {}
    
    url = "https://base.blockscout.com/api/v2/tokens"
    response = requests.get(url,params = params)
    
    if response.status_code == 200:
        
        for item in response.json()['items']:
            tokens[item['name']] = [item['symbol'],item['address'],item['exchange_rate']] # Name : [symbol,address,$]
            
        next_page_params = response.json()['next_page_params']
        
        return tokens, next_page_params
        
    else:
        print(response.text)

def query():

    all_tokens = {}

    # Initialize the first page parameters
    params = {}
    next_page_names = []

    # Fetch and process data in a loop
    while True:
        tokens, next_page_params = get_data(params)
        all_tokens |= tokens  # Use `|=` to merge dictionaries in-place
        print(len(tokens))
        print("------------------")
        
        # Break the loop if there are no more pages
        name = next_page_params['name']
        if name not in next_page_names:
            next_page_names.append(name)
        else:
            break
        
        # Update params for the next page
        params = next_page_params
        
    print("program complete")

    return all_tokens    

def xform_data(all_tokens):
    names = list(all_tokens.keys())
    symbols = [all_tokens[key][0] for key in names]
    addresses = [all_tokens[key][1] for key in names]
    values = [all_tokens[key][2] for key in names]
    data = {'Name': names, 'Symbols':symbols, 'Address':addresses, 'Value': values}

    return data
