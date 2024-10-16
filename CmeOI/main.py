import get_cme_data
import get_table
import post_telegram
import os


tokens = ["BTC",'ETH']
folder_directory = os.getcwd()

def run_main():
    for token in tokens:
        df = get_cme_data.query_data(token)
        image_path = get_table.data_to_png(df,folder_directory,token)
        caption = f"CME Future OI for {token}"
        post_telegram.send_photo_telegram(image_path, caption)



