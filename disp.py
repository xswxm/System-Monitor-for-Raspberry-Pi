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
RST = 21
DC = 26
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

# Load default font.
font = ImageFont.load_default()

# Load customized font.
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def create_background():
    '''Create an image background.
    '''
    # Make sure to create image with mode '1' for 1-bit color.
    img = Image.new('1', (width, height))
    # Create drawing object.
    draw = ImageDraw.Draw(img)
    # Draw background
    # Memory Pie
    draw.arc([(0,0), (30,30)], 0, 360, fill=255)
    # Network Send
    draw.polygon([(122,32), (127,37), (117,37)], outline=255, fill=255)
    draw.rectangle((120,37,124,44), outline=255, fill=255)
    # Network Receive
    draw.rectangle((120,57,124,50), outline=255, fill=255)
    draw.polygon([(122,62), (127,57), (117,57)], outline=255, fill=255)
    # Disk
    draw.rectangle((0, 60, 51, 63), outline=255, fill=0)
    # CPU
    draw.rectangle((94, 0, 127, 30), outline=255, fill=0)
    return img

# Create a background image
image_bg = create_background()

def align_text(msg, x, status=1):
    '''Adjust word Alignment.
    @param: text to align
    @param: position of text
    @param: align method (default 1)
    '''
    # Right alignment
    if status == 1:
        x -= len(msg)*6
    # Middle alignment
    elif status == 0:
        x -= len(msg)*3
    # Left alignment
    return x

def unit_adjust(value):
    '''Adjust unit: B, KB, MB, GB.
    @param: value
    '''
    value = float(value)
    if value < 1024:
        return '{0:.0f}'.format(value) + ' B'
    else:
        value = value / 1024
        if value < 1024:
            return '{0:.1f}'.format(value) + ' KB'
        else:
            value = value / 1024
            if value < 1024:
                return '{0:.1f}'.format(value) + ' MB'
            else:
                value = value / 1024
                return '{0:.1f}'.format(value) + ' GB'

# Initilize network status
netio = psutil.net_io_counters()
netio_sent_val = netio.bytes_sent
netio_recv_val = netio.bytes_recv

# Initilize cpu percentange usages
cpu_pcts = []
# Length of cpu_pcts
cpu_pcts_len = 0

# Create an infinite loop to update display per second
while True:
    # CPU temperature
    cpu_temp = os.popen('vcgencmd measure_temp').readline().replace("temp=", "").replace('\'C', ' \'C').replace('\n', '')
  
    # CPU usage  
    # '1' meaning 1 second
    cpu_pct = psutil.cpu_percent(1)
    if cpu_pcts_len == 32:
        del cpu_pcts[0]
    else:
        cpu_pcts_len = len(cpu_pcts) + 1
    cpu_pcts.append(cpu_pct)
    cpu_pct = 'CPU ' + str(cpu_pct) + ' %'

    # Memory usage
    mem_total, mem_used = os.popen("free -m | awk '/Mem/ {print $2; print $3}'")
    mem_pie = int(mem_used) * 360 / int(mem_total) - 90
    mem_pct = 'MEM ' + str(int(mem_used) * 100 / int(mem_total)) + ' %'
    # mem_total = mem_total.replace('\n', '')
    # mem_used = mem_used.replace('\n', '')

    # Network usage
    netio = psutil.net_io_counters()
    # Compute net upload and download speed
    # The reason we do not calculate with the time is becuase reading cpu usage takes appropriately 1 second
    netio_sent_speed = unit_adjust(netio.bytes_sent-netio_sent_val) + '/S'
    netio_recv_speed = unit_adjust(netio.bytes_recv-netio_recv_val) + '/S'
    # Renew netio values
    netio_sent_val = netio.bytes_sent
    netio_recv_val = netio.bytes_recv
    # String values
    netio_sent_total = unit_adjust(netio_sent_val)
    netio_recv_total = unit_adjust(netio_recv_val)

    # Disk usage
    disk_used, disk_total, disk_pct = os.popen("df -h | awk '/root/ {print $3; print $2; print $5}'")
    disk = '{0}/{1} GB'.format(disk_used.replace('G', ''), disk_total.replace('G', '')).replace('\n', '')
    disk_pct_val = int(disk_pct.replace('%\n', ''))
    disk_pct = 'DISK ' + disk_pct.replace('\n', '')

    # Create image buffer
    image = image_bg.copy()
    draw = ImageDraw.Draw(image)

    # Draw memory usage
    draw.pieslice([(0,0), (30,30)], -90, mem_pie, fill=255)

    # Generate CPU usage points
    cpu_uses = [(126, 29-int(cpu_pcts[-1]*28/100))]
    for i in range(cpu_pcts_len-2,-1,-1):
        p = 29-int(cpu_pcts[i]*28/100)
        distance = p - cpu_uses[-1][1]
        if distance > 1:
            for d in range(1,distance):
               cpu_uses.append((128+i-cpu_pcts_len, p-d))
        elif distance < -1:
            for d in range(1,-distance):
               cpu_uses.append((128+i-cpu_pcts_len, p+d))
        cpu_uses.append((127+i-cpu_pcts_len, p))
    # Draw CPU usage
    draw.point(cpu_uses, fill=255)

    # Draw disk usage
    draw.rectangle((0, 60, disk_pct_val/2, 63), outline=255, fill=255)

    # Draw texts
    draw.text((0, 34),                                   disk_pct,         font=font, fill=255)
    draw.text((0, 46),                                   disk,             font=font, fill=255)
    draw.text((align_text(cpu_temp,62,0), 9),            cpu_temp,         font=font, fill=255)
    draw.text((align_text(cpu_pct,62,0), 18),            cpu_pct,          font=font, fill=255)
    draw.text((align_text(mem_pct,62,0), 0),             mem_pct,          font=font, fill=255)
    draw.text((align_text(netio_sent_speed, 116,1), 30), netio_sent_speed, font=font, fill=255)
    draw.text((align_text(netio_sent_total, 116,1), 38), netio_sent_total, font=font, fill=255)
    draw.text((align_text(netio_recv_speed, 116,1), 46), netio_recv_speed, font=font, fill=255)
    draw.text((align_text(netio_recv_total, 116,1), 54), netio_recv_total, font=font, fill=255)

    # Display image
    disp.image(image)
    disp.display()
