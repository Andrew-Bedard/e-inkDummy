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

# Initialize lists to store prices
btc_prices = []
eth_prices = []
timestamps = []

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

# Update e-ink display with prices and graph
def update_display(epd, btc_price, eth_price):
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    # Draw current prices
    draw.text((10, 10), 'BTC:', font=font24, fill=0)
    draw.text((10, 40), f'${btc_price:.2f}', font=font24, fill=0)
    draw.text((10, 80), 'ETH:', font=font24, fill=0)
    draw.text((10, 110), f'${eth_price:.2f}', font=font24, fill=0)

    # Draw graph
    max_points = 50
    if len(btc_prices) > max_points:
        btc_prices.pop(0)
        eth_prices.pop(0)
        timestamps.pop(0)

    btc_prices.append(btc_price)
    eth_prices.append(eth_price)
    timestamps.append(time.time())

    if len(btc_prices) > 1:
        max_btc = max(btc_prices)
        min_btc = min(btc_prices)
        max_eth = max(eth_prices)
        min_eth = min(eth_prices)

        graph_width = epd.width - 130
        graph_height = epd.height // 2 - 20
        graph_x = 120
        graph_y = 10

        # Draw BTC graph
        draw.text((graph_x, graph_y - 20), 'BTC Price', font=font18, fill=0)
        for i in range(len(btc_prices) - 1):
            x1 = graph_x + i * (graph_width / (len(btc_prices) - 1))
            y1 = graph_y + graph_height - (btc_prices[i] - min_btc) / (max_btc - min_btc) * graph_height
            x2 = graph_x + (i + 1) * (graph_width / (len(btc_prices) - 1))
            y2 = graph_y + graph_height - (btc_prices[i + 1] - min_btc) / (max_btc - min_btc) * graph_height
            draw.line([x1, y1, x2, y2], fill=0)

        # Draw ETH graph
        draw.text((graph_x, graph_y + graph_height + 10), 'ETH Price', font=font18, fill=0)
        for i in range(len(eth_prices) - 1):
            x1 = graph_x + i * (graph_width / (len(eth_prices) - 1))
            y1 = graph_y + graph_height + 30 + graph_height - (eth_prices[i] - min_eth) / (max_eth - min_eth) * graph_height
            x2 = graph_x + (i + 1) * (graph_width / (len(eth_prices) - 1))
            y2 = graph_y + graph_height + 30 + graph_height - (eth_prices[i + 1] - min_eth) / (max_eth - min_eth) * graph_height
            draw.line([x1, y1, x2, y2], fill=0)

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
            time.sleep(600)  # Update every 10 minute

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit(cleanup=True)
        exit()
    except Exception as e:
        logging.error(e)
        epd4in2.epdconfig.module_exit(cleanup=True)

if __name__ == "__main__":
    main()
