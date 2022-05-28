# RPi-status-on-OLED #

To provide the Status of your Raspberry (tested on Zero, 2, 3 and 4) to an ST7735S OLED Display.

I use this script to get a quick and up-to-date status of the system every time I walk past my Raspberry Pis.
In this way I can see at a glance the current workload, whether problems are looming and whether the service is currently running.

My Raspberrys are mounted in my 19Rack:
![Raspberry Pis im Rack](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/raspberrysinrack.jpg)

## Example ##

![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/before_2020-09.png)
![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/before_2021-06.png)
![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/newest.png)
```
* DATE: current date
* IP: IP Address of Pi
* PING: status of ping to local and remote adress
* MAIN: kind of mainboard
* CPU: usage of CPU
* RAM: usage of RAM (the red/green/blue bars stands for GPU advised RAM)
* GPU: size of GPU reserved memory
* TEMP: temperatur of CPU (switched to yellow or red in hotter case)
* SD: current used size and full size of sd card. changed in purple in case your sd it oversize. change in red in case of near of size limit
* IMG: name of newest Backup image
```

## Installation ##
install all needed packages to prepare the software environtent of your Raspberry Pi:
```bash
sudo raspi-config
  and enable Interface type SPI
```
![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/enable_spi.gif)
```bash
sudo apt install python3-pip python3-pil git libatlas-base-dev
sudo pip3 install RPi.GPIO psutil numpy netifaces spidev
```
and this tool itself:
```bash
cd /opt
sudo git clone https://github.com/Starwhooper/RPi-status-on-OLED
```

OPTIONAL: if you with to get some beauty fonts, to use them to show a prettier hostname, do this:
```bash
sudo apt install ttf-mscorefonts-installer
```

## First configurtion ##
```bash
sudo cp /opt/RPi-status-on-OLED/config.json.example /opt/RPi-status-on-OLED/config.json
sudo nano /opt/RPi-status-on-OLED/config.json
```
Check https://github.com/Starwhooper/RPi-status-on-OLED/wiki/explain-config.json to get more details about the config.json file

## Start ##
add it to rc.local to autostart as boot
```bash
sudo nano /etc/rc.local
/opt/RPi-status-on-OLED/status.py
```

## Update ##
If you already use it, feel free to update with
```bash
cd /opt/RPi-status-on-OLED
sudo git pull origin main
```

## Hardware ##
### Display ###
In case you choose waveshare 1.44inch LCD HAT https://www.waveshare.com/wiki/1.44inch_LCD_HAT, you have to wire 1:1 following ports:
* Raspberry Pin 1 (3,3V)
* Raspberry Pin 6 (Ground)
* Raspberry Pin 13 (GPIO 27)
* Raspberry Pin 18 (GPIO 24)
* Raspberry Pin 19 (SPI0 MOSI GPIO 10)
* Raspberry Pin 22 (GPIO 25)
* Raspberry Pin 23 (SPI0 SCLK GPIO 11)
* Raspberry Pin 24 (SPI0 CE0 GPIO 8)


### Case ###
![Display](https://cdn.thingiverse.com/assets/b8/cf/98/25/7c/featured_preview_RPiRack_with_lcd_and_fan.png)
Your can get the STL File and more details regarding the Hardware here: https://www.thingiverse.com/thing:4879316
