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
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,fetch-ai,filecoin,the-graph,polkadot&vs_currencies=usd&include_24hr_change=true'

# Fetch cryptocurrency prices with retry mechanism
def fetch_prices():
    for _ in range(5):  # Retry up to 5 times
        try:
            response = requests.get(COINGECKO_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            btc_price = data['bitcoin']['usd']
            btc_change = data['bitcoin']['usd_24h_change']
            eth_price = data['ethereum']['usd']
            eth_change = data['ethereum']['usd_24h_change']
            fet_price = data['fetch-ai']['usd']
            fet_change = data['fetch-ai']['usd_24h_change']
            fil_price = data['filecoin']['usd']
            fil_change = data['filecoin']['usd_24h_change']
            grt_price = data['the-graph']['usd']
            grt_change = data['the-graph']['usd_24h_change']
            dot_price = data['polkadot']['usd']
            dot_change = data['polkadot']['usd_24h_change']
            return [
                ('BTC', btc_price, btc_change),
                ('ETH', eth_price, eth_change),
                ('FET', fet_price, fet_change),
                ('FIL', fil_price, fil_change),
                ('GRT', grt_price, grt_change),
                ('DOT', dot_price, dot_change)
            ]
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            time.sleep(20)  # Wait 20 seconds before retrying
    return []

# Draw the progress wheel
def draw_progress_wheel(draw, x, y, minute):
    for i in range(10):
        angle_start = i * 36
        angle_end = angle_start + 36
        color = 0 if i < minute else 255
        draw.pieslice([(x-10, y-10), (x+10, y+10)], start=angle_start, end=angle_end, fill=color, outline=0)

# Update e-ink display with prices and changes
def update_display(epd, prices_changes, minute):
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    # Draw header
    draw.text((10, 0), 'Asset/Price', font=font24, fill=0)
    draw.text((210, 0), '24hr Change', font=font24, fill=0)

    # Draw horizontal line
    draw.line((10, 30, epd.width - 10, 30), fill=0)

    # Helper function to draw price and change with delta symbol
    def draw_price_change(x, y, label, price, change):
        draw.text((x, y), f'{label}: ${price:.2f}', font=font24, fill=0)
        change_text = f'{change:.2f}%'
        delta = 'Δ' if change > 0 else '∇'
        change_x = x + 200
        change_color = 0 if change > 0 else 0
        draw.text((change_x, y), f'{delta} {change_text}', font=font18, fill=change_color)

    labels = ['BTC', 'ETH', 'FET', 'FIL', 'GRT', 'DOT']
    y_positions = [40, 70, 100, 130, 160, 190]

    for i, (label, price, change) in enumerate(prices_changes):
        draw_price_change(10, y_positions[i], label, price, change)

    # Draw progress wheel
    draw_progress_wheel(draw, epd.width - 20, epd.height - 20, minute)

    epd.display(epd.getbuffer(Himage))

# Main function
def main():
    logging.info("epd4in2 Crypto Prices with 24h Change")

    epd = epd4in2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    try:
        prices_changes = fetch_prices()
        for minute in range(10):
            update_display(epd, prices_changes, minute)
            time.sleep(60)  # Update every 1 minute
        while True:
            prices_changes = fetch_prices()
            for minute in range(10):
                update_display(epd, prices_changes, minute)
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
