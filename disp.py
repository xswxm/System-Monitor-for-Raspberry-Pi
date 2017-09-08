#!/usr/bin/python
# -*- encoding: utf-8 -*-

import math
# import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import os, psutil

# Raspberry Pi pin configuration:
RST = 25
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Initialize library.
disp.begin()

# Get display width and height.
width = disp.width
height = disp.height

# Clear display.
disp.clear()
disp.display()

# Create image buffer.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (width, height))

# Load default font.
font = ImageFont.load_default()

# Load customized font
# font = ImageFont.truetype('Minecraftia.ttf', 8)

# Create drawing object.
draw = ImageDraw.Draw(image)

def indent(msg, length):
    for i in range(length - len(msg) + 1):
        msg = ' ' + msg
    return msg

def speed_adjust(value):
    if value < 1024:
        return '{0:.0f}'.format(value) + ' B/S'
    else:
        value = value / 1024
        if value < 1024:
            return '{0:.2f}'.format(value) + ' KB/S'
        else:
            value = value / 1024
            return '{0:.2f}'.format(value) + ' MB/S'

# # Initialize time
# time_new = time_old = time.time()

# Initilize network status
netio = psutil.net_io_counters()
netio_sent = netio.bytes_sent
netio_recv = netio.bytes_recv

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    # IP
    IP = os.popen("hostname -I | cut -d\' \' -f1").readline()
    # CPU temperature and usage
    cpu_temp = os.popen('vcgencmd measure_temp').readline().replace("temp=", "").replace('\'C', ' \'C')
    # '1' meaning 1 second
    cpu_used = psutil.cpu_percent(1)
    draw.rectangle((0, 60, 127, 63), outline=255, fill=0)
    draw.rectangle((0, 60, int(1.28 * cpu_used), 63), outline=255, fill=255)
    cpu_used = str(cpu_used) + ' %'
    # Memory usage
    mem_total, mem_used = os.popen("free -m | awk '/Mem/ {print $2; print $3}'")
    mem  = '{0}/{1} MB'.format(mem_used, mem_total).replace('\n', '')
    mem_per = str(int(mem_used) * 100 / int(mem_total)) + ' %'
    # Network usage
    netio = psutil.net_io_counters()
    # # Update time
    # time_new = time.time()
    # # Calculate time passed
    # t = time_new - time_old
    # Calculate net upload and download speed
    # The reason we do not calculate with the time is becuase reading cpu usage takes appropriately 1 second
    # Otherwise, please add time to the calculation
    net_up = speed_adjust(float(netio.bytes_sent-netio_sent))
    net_down = speed_adjust(float(netio.bytes_recv-netio_recv))
    # # Renew time_old
    # time_old = time.time()
    # Renew netio values
    netio_sent = netio.bytes_sent
    netio_recv = netio.bytes_recv
    # # Renew time_old
    # time_old = time.time()
    # Disk usage
    disk_used, disk_total, disk_per = os.popen("df -h | awk '/root/ {print $3; print $2; print $5}'")
    disk = '{0}/{1} GB'.format(disk_used.replace('G', ''), disk_total.replace('G', '')).replace('\n', '')
    disk_per = disk_per.replace('%', ' %')
    # HDD usage
    try:
        sda1_used, sda1_total, sda1_per = os.popen("df -h | awk '/sda1/ {print $3; print $2; print $5}'")
        sda1 = '{0}/{1} GB'.format(sda1_used.replace('G', ''), sda1_total.replace('G', '')).replace('\n', '')
        sda1_per = sda1_per.replace('%', ' %')
    # Exception if there is no sda driver
    except Exception as e:
        sda1 = 'N/A'
        sda1_per = 'N/A'
    # sda1_used, sda1_total, sda1_per = os.popen("df -h | awk '/sda1/ {print $3; print $2; print $5}'")
    # sda1 = sda1_used.replace('G', '') + '/' + sda1_total.replace('G', '') + ' GB'
    # sda1_per = sda1_per.replace('%', ' %')

    # Draw titles
    draw.text((0, 0),  'IP:',       font=font, fill=255)
    draw.text((0, 8),  'CPU:',      font=font, fill=255)
    draw.text((0, 16), 'Mem:',      font=font, fill=255)
    draw.text((0, 24), 'Upload:',   font=font, fill=255)
    draw.text((0, 32), 'Download:', font=font, fill=255)
    draw.text((0, 40), 'Disk:',      font=font, fill=255)
    draw.text((0, 48), 'HDD:',      font=font, fill=255)
    # Draw statistics
    draw.text((38, 0),  indent(IP, 15),       font=font, fill=255)
    draw.text((38, 8),  cpu_temp,             font=font, fill=255)
    draw.text((86, 8),  indent(cpu_used, 6),  font=font, fill=255)
    draw.text((38, 16), mem,                  font=font, fill=255)
    draw.text((98, 16), indent(mem_per, 4),   font=font, fill=255)
    draw.text((56, 24), indent(net_up, 11),   font=font, fill=255)
    draw.text((56, 32), indent(net_down, 11), font=font, fill=255)
    draw.text((34, 40), disk,                 font=font, fill=255)
    draw.text((98, 40), indent(disk_per, 5),  font=font, fill=255)
    draw.text((34, 48), sda1,                 font=font, fill=255)
    draw.text((98, 48), indent(sda1_per, 5),  font=font, fill=255)
    

    # Display image.
    disp.image(image)
    disp.display()
