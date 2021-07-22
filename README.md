# RPi-status-on-OLED #

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
sudo apt-get update && sudo apt-get upgrade && sudo apt-get install python3-pip python3-pil git libatlas-base-dev ttf-mscorefonts-installer
sudo pip3 install RPi.GPIO psutil numpy
```
and this tool itself:
```bash
cd /opt
sudo git clone https://github.com/Starwhooper/RPi-status-on-OLED
```

## First configurtion ##
```bash
sudo cp /opt/RPi-status-on-OLED/config.json.example /opt/RPi-status-on-OLED/config.json
sudo nano /opt/RPi-status-on-OLED/config.json
```

## Start ##
Its also able to add it in cron via ```crontab -e```, it prevent doublicate starts
```bash
/opt/RPi-status-on-OLED/status.py
```

## Case ##
![Display](https://cdn.thingiverse.com/assets/b8/cf/98/25/7c/featured_preview_RPiRack_with_lcd_and_fan.png)
Your can get the STL File and more details regarding the Hardware here: https://www.thingiverse.com/thing:4879316







