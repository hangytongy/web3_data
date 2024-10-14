import requests
import pandas as pd
import matplotlib.pyplot as plt

url = 'https://stablecoins.llama.fi/stablecoins'
params = {'includePrices' : 'true'}

response = requests.get(url, params=params)

df = pd.DataFrame(response.json()['peggedAssets'])

def get_supply(x):
    if isinstance(x, dict) and 'peggedUSD' in x:
        return float(x['peggedUSD'])
    return None 

df['circulating'] = df['circulating'].apply(get_supply)
df['circulatingPrevDay'] = df['circulatingPrevDay'].apply(get_supply)
df['circulatingPrevWeek'] = df['circulatingPrevWeek'].apply(get_supply)
df['circulatingPrevMonth'] = df['circulatingPrevMonth'].apply(get_supply)

df.sort_values(by = ['circulating'], ascending = False, inplace = True)
df = df.reset_index()
df = df[['name','symbol','circulating','circulatingPrevDay','circulatingPrevWeek','circulatingPrevMonth']]

def calculate_percentage_change(current, previous):
    return ((previous - current) / current) * 100

df['circulatingPrevDay_change'] = calculate_percentage_change(df['circulating'], df['circulatingPrevDay'])
df['circulatingPrevWeek_change'] = calculate_percentage_change(df['circulating'], df['circulatingPrevWeek'])
df['circulatingPrevMonth_change'] = calculate_percentage_change(df['circulating'], df['circulatingPrevMonth'])

circulating_sum = df['circulating'].sum()
circulatingPrevDay_sum = df['circulatingPrevDay'].sum()
circulatingPrevWeek_sum = df['circulatingPrevWeek'].sum()
circulatingPrevMonth_sum = df['circulatingPrevMonth'].sum()

df_change = df[['name','symbol','circulatingPrevDay_change','circulatingPrevWeek_change','circulatingPrevMonth_change']]

df_change_top10 = df_change[0:9]

print(df_change_top10)

# Plotting the DataFrame
fig, ax = plt.subplots(figsize=(5, 2))  # Adjust the size as needed
ax.axis('tight')
ax.axis('off')
table_data = ax.table(cellText=df_change_top10.values, colLabels=df_change_top10.columns, cellLoc='center', loc='center')

# Save the figure
plt.savefig('dataframe.png', bbox_inches='tight', dpi=300)
plt.close()
