import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont

# Pin configuration
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24

# SPI configuration
SPI_CHANNEL = 0
SPI_DEVICE = 0

# Initialize SPI
spi = spidev.SpiDev()
spi.open(SPI_CHANNEL, SPI_DEVICE)
spi.max_speed_hz = 2000000

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def spi_writebyte(data):
    spi.writebytes(data)

def reset():
    digital_write(RST_PIN, 1)
    time.sleep(0.2)
    digital_write(RST_PIN, 0)
    time.sleep(0.2)
    digital_write(RST_PIN, 1)
    time.sleep(0.2)

def send_command(command):
    digital_write(DC_PIN, 0)
    digital_write(CS_PIN, 0)
    spi_writebyte([command])
    digital_write(CS_PIN, 1)

def send_data(data):
    digital_write(DC_PIN, 1)
    digital_write(CS_PIN, 0)
    spi_writebyte([data])
    digital_write(CS_PIN, 1)

def init_display():
    reset()
    # Send initialization commands to the e-ink display
    send_command(0x01)  # Power setting
    send_data(0x03)
    send_data(0x00)
    send_data(0x2b)
    send_data(0x2b)
    send_command(0x06)  # Booster soft start
    send_data(0x17)
    send_data(0x17)
    send_data(0x17)
    send_command(0x04)  # Power on
    while digital_read(BUSY_PIN) == 1:
        time.sleep(0.1)
    send_command(0x00)  # Panel setting
    send_data(0xbf)
    send_data(0x0d)
    send_command(0x30)  # PLL control
    send_data(0x3a)
    send_command(0x61)  # Resolution setting
    send_data(0x02)
    send_data(0x88)
    send_data(0x01)
    send_data(0xec)
    send_command(0x82)  # VCOM DC setting
    send_data(0x28)
    send_command(0x50)  # VCOM and data interval setting
    send_data(0x97)

def clear_display():
    # Clear the display buffer
    send_command(0x10)
    for _ in range(176 * 264 // 8):
        send_data(0x00)
    update_display()

def update_display():
    # Trigger the display update
    send_command(0x12)
    while digital_read(BUSY_PIN) == 1:  # Wait until the display is not busy
        time.sleep(0.1)

def display_image(image):
    # Convert image to black and white
    bw_image = image.convert('1')
    pixels = bw_image.load()

    # Send the image data to the display
    send_command(0x10)
    for y in range(bw_image.height):
        for x in range(0, bw_image.width, 8):
            byte = 0x00
            for bit in range(8):
                if x + bit < bw_image.width and pixels[x + bit, y] == 0:
                    byte |= (1 << (7 - bit))
            send_data(byte)
    update_display()

def create_image_with_text(text):
    width, height = 264, 176  # Change these values based on your display resolution
    image = Image.new('1', (width, height), 255)  # Create a blank white image
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # Load a default font

    # Calculate text size and position
    text_width, text_height = draw.textsize(text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text on the image
    draw.text((x, y), text, font=font, fill=0)

    return image

try:
    init_display()
    clear_display()
    image = create_image_with_text("Hello, World!")
    display_image(image)
finally:
    GPIO.cleanup()
