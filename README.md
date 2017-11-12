System Monitor for Raspberry Pi with 12864/SSD1306

### Demo
<img src="https://github.com/xswxm/System-Monitor-for-Raspberry-Pi/blob/master/demo.bmp?raw=true" 
alt="Demo" width="512" height="256" border="10" />

### Modules
Adafruit_GPIO.SPI
Adafruit_SSD1306
psutil

### Setting Up
Configure your 128464 by following this tutorial: https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/usage?view=all

Install additional modules
```sh
sudo apt-get install python-pip
sudo pip install psutil
```

Edit the script. Replace the ports to yours
```python
# Ports used for fthe Display. You may have to change them to yours
RST = 25
DC = 24
```

### How to Use
```sh
# Run with Python 2
python disp.py
```

License
----
MIT
