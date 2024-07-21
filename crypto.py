#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
import requests
from PIL import Image, ImageDraw, ImageFont

# Set up paths
base_dir = os.path.dirname(os.path.realpath(__file__))
picdir = os.path.join(base_dir, 'pic')
libdir = os.path.join(base_dir, 'lib')
sys.path.append(libdir)

from waveshare_epd import epd4in2

logging.basicConfig(level=logging.DEBUG)

# API URL
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'

# Fetch cryptocurrency prices
def fetch_prices():
    try:
        response = requests.get(COINGECKO_API_URL)
        response.raise_for_status()
        data = response.json()
        btc_price = data['bitcoin']['usd']
        eth_price = data['ethereum']['usd']
        return btc_price, eth_price
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None, None

# Update e-ink display with prices
def update_display(epd, btc_price, eth_price):
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    
    draw.text((10, 10), 'BTC:', font=font24, fill=0)
    draw.text((10, 40), f'${btc_price:.2f}', font=font24, fill=0)
    draw.text((10, 80), 'ETH:', font=font24, fill=0)
    draw.text((10, 110), f'${eth_price:.2f}', font=font24, fill=0)

    epd.display(epd.getbuffer(Himage))

# Main function
def main():
    logging.info("epd4in2 Bitcoin and Ethereum Prices")

    epd = epd4in2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    try:
        while True:
            btc_price, eth_price = fetch_prices()
            if btc_price is not None and eth_price is not None:
                update_display(epd, btc_price, eth_price)
            time.sleep(60*5)  # Update every 1 minute

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit(cleanup=True)
        exit()
    except Exception as e:
        logging.error(e)
        epd4in2.epdconfig.module_exit(cleanup=True)

if __name__ == "__main__":
    main()
