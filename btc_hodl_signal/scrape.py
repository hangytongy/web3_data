import requests
from datetime import datetime
import pandas as pd
import os

import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from PIL import Image

def scrape_web(website,class_name):
    print("launch chrome")
    
    chrome_driver_path = os.getenv("chromepath")  #"C:\Program Files (x86)\chromedriver.exe" #replace with actual path
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--no-sandbox")  # Required for some environments
    chrome_options.add_argument("--disable-dev-shm-usage") 
    
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    
    try:
        driver.get(website)
        time.sleep(10)
        element = driver.find_element(By.CLASS_NAME, class_name)
        element_screenshot_path = f'element_screenshot_{class_name}.png'
        element.screenshot(element_screenshot_path)
        print(f'Screenshot of element saved to {element_screenshot_path}')
        return element_screenshot_path
    finally:
        driver.quit()
        
def combine_image(pic_path):
    
    output_path = "combined_img.png"
    
    images = [Image.open(pic) for pic in pic_path]
    
    # Calculate the total width and height for the combined image
    combined_width = max(image.width for image in images)  # Take the widest image's width
    combined_height = sum(image.height for image in images)  # Sum of all images' heights
    
    # Create a new blank image with the calculated combined width and height
    combined_image = Image.new("RGB", (combined_width, combined_height))

    # Paste each image below the previous one
    current_height = 0
    for image in images:
        combined_image.paste(image, (0, current_height))
        current_height += image.height  # Update the current height for the next image

    # Save the final combined image
    combined_image.save(output_path)
    print(f'Combined image saved to {output_path}')
    return output_path

    
