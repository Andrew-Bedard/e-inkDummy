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
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true'

# Fetch cryptocurrency prices
def fetch_prices():
    try:
        response = requests.get(COINGECKO_API_URL)
        response.raise_for_status()
        data = response.json()
        btc_price = data['bitcoin']['usd']
        btc_change = data['bitcoin']['usd_24h_change']
        eth_price = data['ethereum']['usd']
        eth_change = data['ethereum']['usd_24h_change']
        return btc_price, btc_change, eth_price, eth_change
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None, None, None, None

# Update e-ink display with prices and changes
def update_display(epd, btc_price, btc_change, eth_price, eth_change):
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    # Helper function to draw price and change with arrow
    def draw_price_change(x, y, label, price, change):
        draw.text((x, y), f'{label}: ${price:.2f}', font=font24, fill=0)
        change_text = f'{change:.2f}%'
        arrow = '↑' if change > 0 else '↓'
        change_x = x + 200
        change_color = 0 if change > 0 else 0
        draw.text((change_x, y), f'{arrow} {change_text}', font=font24, fill=change_color)

    # Draw BTC price and change
    draw_price_change(10, 10, 'BTC', btc_price, btc_change)

    # Draw ETH price and change
    draw_price_change(10, 50, 'ETH', eth_price, eth_change)

    epd.display(epd.getbuffer(Himage))

# Main function
def main():
    logging.info("epd4in2 Bitcoin and Ethereum Prices with 24h Change")

    epd = epd4in2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    try:
        while True:
            btc_price, btc_change, eth_price, eth_change = fetch_prices()
            if btc_price is not None and eth_price is not None:
                update_display(epd, btc_price, btc_change, eth_price, eth_change)
            time.sleep(60)  # Update every 1 minute

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit(cleanup=True)
        exit()
    except Exception as e:
        logging.error(e)
        epd4in2.epdconfig.module_exit(cleanup=True)

if __name__ == "__main__":
    main()
