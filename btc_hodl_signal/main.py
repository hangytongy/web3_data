import scrape
from post_telegram import send_photo_telegram

def run_main():
    website = "https://www.bitcoinmagazinepro.com/charts/realized-cap-hodl-waves/"
    class_names = ["main-svg","legend"]

    pic_path = []
    for class_name in class_names:
        pic = scrape.scrape_web(website,class_name)
        pic_path.append(pic)
        
    output = scrape.combine_image(pic_path)

    send_photo_telegram(output,"BTC HODL Signal")