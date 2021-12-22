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
 import sys
 import time
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
 if "wallpaper_enable" in cf.keys():
  if cf["wallpaper_enable"] == "true":
   if "wallpaper_file" in cf.keys():
    if "wallpaper_per_minute" in cf.keys():
     wp_file = os.path.split(os.path.abspath(__file__))[0] + '/' + cf["wallpaper_file"]
     print(os.path.split(os.path.abspath(__file__))[0] + '/' + cf["wallpaper_file"])
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

while True:
#########prepare blank image
 image = Image.new("RGB", (LCD.width, LCD.height), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)

#########show wallpaper instead of regular content
 
 remain = divmod(int(time.strftime('%S')), (60 / cf["wallpaper_per_minute"]))
 if remain[1] == 0 and wp_found == 1:
  image.paste(wp,(move_left,move_top))
 else:

##########add lots of compotents to image
  posx = 0

  ##### check components
  try:
   cf["components"][0]
  except:
   sys.exit('exit: in ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json is no "components" empty, checkout config.json.example')

  sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/component')
  import rpistathelloworld
  import rpistathostname
  import rpistatboard
  import rpistatcpu
  import rpistatcurrentdate
  import rpistatcurrenttime
  import rpistatipping
  import rpistatlastimage
  import rpistatsd
  import rpistatram
  import rpistatos
  import rpistatuptime
  import rpistattemperatur

  for componentname in cf["components"]:

   if componentname == 'helloworld': banner, bannerhight = rpistathelloworld.output(cf,LCD.width)
   if componentname == 'board': banner, bannerhight = rpistatboard.output(cf,LCD.width)
   if componentname == 'hostname': banner, bannerhight = rpistathostname.output(cf,LCD.width)
   if componentname == 'cpu': banner, bannerhight = rpistatcpu.output(cf,LCD.width)
   if componentname == 'currentdate': banner, bannerhight = rpistatcurrentdate.output(cf,LCD.width)
   if componentname == 'currenttime': banner, bannerhight = rpistatcurrenttime.output(cf,LCD.width)
   if componentname == 'ipping': banner, bannerhight = rpistatipping.output(cf,LCD.width)
   if componentname == 'lastimage': banner, bannerhight = rpistatlastimage.output(cf,LCD.width)
   if componentname == 'ram': banner, bannerhight = rpistatram.output(cf,LCD.width)
   if componentname == 'sd': banner, bannerhight = rpistatsd.output(cf,LCD.width)
   if componentname == 'os': banner, bannerhight = rpistatos.output(cf,LCD.width)
   if componentname == 'temperatur': banner, bannerhight = rpistattemperatur.output(cf,LCD.width)
   if componentname == 'uptime': banner, bannerhight = rpistatuptime.output(cf,LCD.width)
   image.paste(banner,(0,posx))
   banner=Image.new("RGB", (1, 1), cf["backgroundcolor"])
   posx = posx + bannerhight
   bannerhight=0

####################################################promt picture to display
 if cf['rotate'] == 90: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_90),0,0)
 elif cf['rotate'] == 180: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_180),0,0)
 elif cf['rotate'] == 270: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_270),0,0)
 else: LCD.LCD_ShowImage(image,0,0)

 time.sleep(int(cf["imagerefresh"]))

 try: lastpicturesave
 except: lastpicturesave = 0

#  print(os.path.isdir(cf["saveimagedestination"]))

 if 'cf["saveimagedestination"]' in locals() and 'cf["picturesaveintervall"]' in locals():
  if int(cf["picturesaveintervall"]) >= 1:
   saveimagedestination = str(cf["saveimagedestination"]).replace("%HOSTNAME%", str(hostname).lower())
   if (os.path.isdir(os.path.dirname(saveimagedestination))) == True:
    try:
     if time.time() >= lastpicturesave + int(cf["picturesaveintervall"]):
      image.save(saveimagedestination,optimize=True)
      lastpicturesave = time.time()
    except:
     print('picture ' + saveimagedestination + 'could not saved')
   else: print('folder ' + os.path.isdir(os.path.dirname(saveimagedestination)) + 'not found')

