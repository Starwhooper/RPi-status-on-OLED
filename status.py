#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-status-on-OLED

#######################################################
#
# Prepare
#
#######################################################

##### check if all required packages are aviable
try:
# from pathlib import Path
 from PIL import Image
 from PIL import ImageDraw
 import json
 import os
 import psutil
 import socket
 import sys
 import time
 import glob
except:
 sys.exit('any needed package is not aviable. Please check README.md to check which components shopuld be installed via pip3".')

##### ensure that only one instance is running at the same time
runninginstances = 0
for p in psutil.process_iter():
 if len(p.cmdline()) == 2:
  if p.cmdline()[0] == '/usr/bin/python3':
   if p.cmdline()[1] == os.path.abspath(__file__):
    runninginstances = runninginstances + 1
if runninginstances >= 2:
 sys.exit('exit: is already running')

##### import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required ')

###### set defaults
#try: cf["fontcolor"];
#except: cf["fontcolor"] = 'WHITE';

#######################################################
#
# Init Screen
#
#######################################################

if cf["lcddriver"] == 'waveshare144':
 sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/lcddriver/' + cf["lcddriver"])
 try:
  import LCD_1in44
  import LCD_Config
 except:
  sys.exit('exit: modules from waveshare not found in ' + os.path.split(os.path.abspath(__file__))[0] + '/lcddriver/' + cf["lcddriver"] + ', or was found but could not load')
 try:
  LCD = LCD_1in44.LCD()
  Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
  LCD.LCD_Init(Lcd_ScanDir)
  LCD.LCD_Clear()
 except:
  sys.exit('LCD could not initialised')

#######################################################
#
# get system informiation only one time at start
#
#######################################################

# try: hostname
# except: hostname = str(socket.gethostname()).upper()
# try: ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
# except: ip = 'noip'
# try: cf["fontcolor"];
# except: cf["fontcolor"] = 'WHITE';

#######################################################
#
# prepare wallpaper
#
#######################################################

wp_seconds = [99]
wp_found = 0
if "wallpaper" in cf.keys():
 if cf["wallpaper"]["enable"] == "true":
  if "file" in cf["wallpaper"].keys():
   if "per_minute" in cf["wallpaper"].keys():
    wp_file = os.path.split(os.path.abspath(__file__))[0] + '/' + cf["wallpaper"]["file"]
    if os.path.isfile(wp_file):
     wp = Image.open(wp_file)
     factor_w = round(100/wp.width * LCD.width)
     factor_h = round(100/wp.height * LCD.height)
     if factor_w <= factor_h:
      new_width = int(wp.width * factor_w / 100)
      new_height = int(wp.height * factor_w / 100)
     else:
      new_width = int(wp.width * factor_h / 100)
      new_height = int(wp.height * factor_h / 100)
     wp = wp.resize((new_width, new_height))
     move_left = int((LCD.width - new_width) / 2)
     move_top = int((LCD.height - new_height) / 2)
     wp_found = 1

#######################################################
#
# import own functions
#
#######################################################

try:
 cf["components"][0]
except:
 sys.exit('exit: in ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json is no "components" empty, checkout config.json.example')

sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/component')
import rpistatboard
import rpistatborder
import rpistatcpu
import rpistatcurrentdate
import rpistatcurrentdatetime
import rpistatcurrenttime
import rpistatdrive
import rpistathelloworld
import rpistathostname
import rpistatipping
import rpistatlastimage
import rpistatos
import rpistatram
import rpistatsd
import rpistattemperatur
import rpistatuptime
import rpistatversion

alert = ''
lastmessage = 0
scroll_y = 0
gab_y = 0
current_gab_y = 0

while True:
#########prepare blank image
 image = Image.new("RGB", (LCD.width, LCD.height), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)

#########show wallpaper instead of regular content
 remain = divmod(int(time.strftime('%S')), (60 / cf["wallpaper"]["per_minute"]))
 if remain[1] == 0 and wp_found == 1:
  image.paste(wp,(move_left,move_top))
 else:
  if current_gab_y < gab_y:
   current_gab_y = current_gab_y + 1
  else: current_gab_y = 0
  posx = 0 - current_gab_y

  overallhight = 0
  
  for componentname in cf["components"]:
   if componentname == 'board': banner, bannerhight = rpistatboard.output(cf,LCD.width)
   if componentname == 'border': banner, bannerhight = rpistatborder.output(cf,LCD.width)
   if componentname == 'cpu': banner, bannerhight = rpistatcpu.output(cf,LCD.width)
   if componentname == 'currentdate': banner, bannerhight = rpistatcurrentdate.output(cf,LCD.width)
   if componentname == 'currentdatetime': banner, bannerhight = rpistatcurrentdatetime.output(cf,LCD.width)
   if componentname == 'currenttime': banner, bannerhight = rpistatcurrenttime.output(cf,LCD.width)
   if componentname == 'drive': banner, bannerhight, alert = rpistatdrive.output(cf,LCD.width)
   if componentname == 'helloworld': banner, bannerhight = rpistathelloworld.output(cf,LCD.width)
   if componentname == 'hostname': banner, bannerhight = rpistathostname.output(cf,LCD.width)
   if componentname == 'ipping': banner, bannerhight = rpistatipping.output(cf,LCD.width)
   if componentname == 'lastimage': banner, bannerhight = rpistatlastimage.output(cf,LCD.width)
   if componentname == 'os': banner, bannerhight = rpistatos.output(cf,LCD.width)
   if componentname == 'ram': banner, bannerhight = rpistatram.output(cf,LCD.width)
   if componentname == 'sd': banner, bannerhight = rpistatsd.output(cf,LCD.width)
   if componentname == 'temperatur': banner, bannerhight = rpistattemperatur.output(cf,LCD.width)
   if componentname == 'uptime': banner, bannerhight = rpistatuptime.output(cf,LCD.width)
   if componentname == 'version': banner, bannerhight = rpistatversion.output(cf,LCD.width)
   image.paste(banner,(0,posx))
   banner=Image.new("RGB", (1, 1), cf["backgroundcolor"])
   posx = posx + bannerhight
   overallhight = overallhight + bannerhight
   bannerhight=0
   
   if len(alert) >= 1:
    if cf["pushover"]["messages"] == 1 and time.time() >= lastmessage + 60 * 60 * 24:
     import requests
     r = requests.post("https://api.pushover.net/1/messages.json", data = {
         "token": cf["pushover"]["apikey"],
         "user": cf["pushover"]["userkey"],
         "html": 1,
         "priority": 1,
         "message": hostname + " " + alert,
         }
     ,
     files = {
      "attachment": ("image.png", open(str(cf["savescreen"]["destination"]).replace("%HOSTNAME%", str(socket.gethostname()).lower()), "rb"), "image/png")
     }
     )
     lastmessage = time.time()
     alert=''

####################################################promt picture to display
 if scroll_y == 0: 
  scroll_y = overallhight
  try: 
   if scroll_y > LCD.height + cf['no_y_scroll_offset']: gab_y = scroll_y - LCD.height
  except:
   if scroll_y > LCD.height: gab_y = scroll_y - LCD.height

 if cf['rotate'] == 90: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_90),0,0)
 elif cf['rotate'] == 180: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_180),0,0)
 elif cf['rotate'] == 270: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_270),0,0)
 else: LCD.LCD_ShowImage(image,0,0)

 time.sleep(float(cf["imagerefresh"]))

 try: lastpicturesave
 except: lastpicturesave = 0

 if 'cf["savescreen"]' in locals() and 'cf["savescreen"]["intervall"]' in locals():
  if int(cf["savescreen"]["intervall"]) >= 1:
   saveimagedestination = str(cf["savescreen"]["destination"]).replace("%HOSTNAME%", str(hostname).lower())
   if (os.path.isdir(os.path.dirname(saveimagedestination))) == True:
    try:
     if time.time() >= lastpicturesave + int(cf["savescreen"]["intervall"]):
      image.save(saveimagedestination,optimize=True)
      lastpicturesave = time.time()
    except:
     print('picture ' + saveimagedestination + 'could not saved')
   else: print('folder ' + os.path.isdir(os.path.dirname(saveimagedestination)) + 'not found')
