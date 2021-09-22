#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-status-on-OLED

from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
import glob
import os
import re
import psutil
import requests
import RPi.GPIO as GPIO
import socket
import sys
import time
import subprocess
import json

##########import special modules and provide special errormessage
try:
 import numpy
except ValueError:
 sys.exit('needed package numpy is not aviable. Try to install it with "sudo pip3 install numpy".')

##########ensure that only one instance is running at the same time
runninginstances = 0
for p in psutil.process_iter():
 if len(p.cmdline()) == 2:
  if p.cmdline()[0] == '/usr/bin/python3':
   if p.cmdline()[1] == os.path.abspath(__file__):
    runninginstances = runninginstances + 1
#    print(p.cmdline()[0])
#    print(p.cmdline()[1])
if runninginstances >= 2:
 sys.exit('exit: is already running')

##########import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required ')
##########set default
try: cf["fontcolor"];
except: cf["fontcolor"] = 'WHITE';

##########import modules from waveshare
if cf["lcddriver"] == 'waveshare144':
 sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/lcddriver/' + cf["lcddriver"])
 try:
  import LCD_1in44
  import LCD_Config
 except:
  sys.exit('exit: modules from waveshare not found in ' + os.path.split(os.path.abspath(__file__))[0] + '/' + cf["lcddriver"] + ', or was found but could not load')

##########check components
try:
 cf["components"][0]
except:
 sys.exit('exit: in ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json is no "components" empty, checkout config.json.example')

def main():
 LCD = LCD_1in44.LCD()
 Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
 LCD.LCD_Init(Lcd_ScanDir)
 LCD.LCD_Clear()

##########set variables for first run
#currently no need :-)

 while True:
##########get system informiation only one time at start
  try: hostname
  except: hostname = str(socket.gethostname()).upper()
  ip = str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

##########prepare blank image
  image = Image.new("RGB", (LCD.width, LCD.height), cf["backgroundcolor"])
  draw = ImageDraw.Draw(image)

  if int(time.strftime('%S')[-1]) == 1:

   wp_file = os.path.split(os.path.abspath(__file__))[0] + '/wp.jpg'
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
   try: image.paste(wp,(move_left,move_top))
   except: 1

  else:

 ##########add lots of compotents to image
   posx = 0

   ##########component hostname
   if 'hostname' in cf["components"]:

    if os.path.isfile(cf["ttffont"]):
     ttffontheader = ImageFont.truetype(cf["ttffont"], 20)
     width, height = draw.textsize(str(hostname), font=ttffontheader)
     draw.text( (((LCD_1in44.LCD_WIDTH-width)/2) , 0), str(hostname), font=ttffontheader, fill = 'YELLOW')
    else:
     width, height = draw.textsize(str(hostname))
     imagehostname = Image.new("RGB", (width, height), "BLACK")
     drawimagehostname = ImageDraw.Draw(imagehostname)
     drawimagehostname.text((0,0), hostname , fill = 'YELLOW')
     factor=2
     imagehostname = imagehostname.resize((int(width*factor), int(height*factor)))
     image.paste(imagehostname,((int((LCD_1in44.LCD_WIDTH-(width*2))/2)),0))
    posx = posx + 14

   ##########component currentdate
   if 'currentdate' in cf["components"]:
    draw.text((0,posx), "Date:" + datetime.date.today().strftime('%a')[:2] + datetime.date.today().strftime(', %d. %b.\'%y') , fill = cf["fontcolor"])
    posx = posx + 10

   ##########component currenttime
   if 'currenttime' in cf["components"]:
    draw.text((0,posx), "Time:" + time.strftime('%H:%M:%S', time.localtime()) , fill = cf["fontcolor"])
    posx = posx + 10

   ##########component ip
   if 'ip' in cf["components"]:
    draw.text((0,posx), "IP  :" + ip , fill = cf["fontcolor"])
    posx = posx + 10

   ##########component ping
   if 'ping' in cf["components"]:
    try: lastping
    except: lastping = 0
    pinglocal = pinginternet = "offline"
    if len(cf["localpingdestination"]) >= 1: localpingdestination = cf["localpingdestination"]
    else: localpingdestination = ip[0:ip.rfind('.')] + '.1'
    if time.time() >= lastping + cf["pingintervall"]: #Ping systems all x seconds
     if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinglocalcolor = 'GREEN'
     else: pinglocalcolor = 'RED'
     if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinginternetcolor = 'GREEN'
     else: pinginternetcolor = 'RED'
     lastping = int(time.time())
    draw.rectangle((0, posx + 11) + (int( LCD_1in44.LCD_WIDTH / cf["pingintervall"] * (int(time.time()) - lastping)), posx + 12), fill="GREEN", width=1)
    draw.text((0,posx), "Ping:     ,", fill = cf["fontcolor"])
    draw.text((0,posx), "     LOCAL", fill = pinglocalcolor)
    draw.text((0,posx), "           REMOTE", fill = pinginternetcolor)
    posx = posx + 13

   ##########component ipping
   if 'ipping' in cf["components"]:
    draw.text((0,posx), "IP  :" + ip , fill = cf["fontcolor"])
    try: lastping
    except: lastping = 0
    pinglocal = pinginternet = "offline"
    if len(cf["localpingdestination"]) >= 1: localpingdestination = cf["localpingdestination"]
    else: localpingdestination = ip[0:ip.rfind('.')] + '.1'
    if time.time() >= lastping + cf["pingintervall"]: #Ping systems all x seconds
     if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinglocalcolor = 'GREEN'
     else: pinglocalcolor = 'RED'
     if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinginternetcolor = 'GREEN'
     else: pinginternetcolor = 'RED'
     lastping = int(time.time())
    draw.rectangle((0, posx + 11) + (int( LCD_1in44.LCD_WIDTH / cf["pingintervall"] * (int(time.time()) - lastping)), posx + 12), fill="GREEN", width=1)
    draw.text((0,posx), "  L", fill = pinglocalcolor)
    draw.text((0,posx), "   R", fill = pinginternetcolor)
    posx = posx + 13

   ##########component board
   if 'board' in cf["components"]:
    if 'piboardinformation' not in locals():
     fobj = open("/sys/firmware/devicetree/base/model")
     output = ''
     for line in fobj:
        output = output + line.rstrip()
     fobj.close()
     output = output.replace("Raspberry Pi ", "RPi ")
     output = output.replace(" Model ", "")
     output = output.replace("Rev ", "")
     output = output.replace("  ", " ")
     output = re.sub('[^a-zA-Z0-9. ]+', '', output)
     piboardinformation = output
    draw.text((0,posx), "Main:" + piboardinformation, fill = cf["fontcolor"])
    posx = posx + 10

   ##########component cpu
   if 'cpu' in cf["components"]:
    usage = int(float(psutil.cpu_percent()))
    draw.text((0,posx), "CPU :", fill = cf["fontcolor"])
    width = (LCD_1in44.LCD_WIDTH - 1 - cf["boxmarginleft"] ) /100 * usage
    fontcolor = 'WHITE'
    if usage >= 80: fillcolor = 'RED'
    elif usage >= 60: fillcolor = 'YELLOW'
    else: fillcolor = 'GREEN'
    if fillcolor == 'YELLOW': fontcolor = 'GREY'
    draw.rectangle((cf["boxmarginleft"], posx) + (cf["boxmarginleft"] + width, posx + 10), fill=fillcolor, width=0)
    draw.rectangle((cf["boxmarginleft"], posx) + (LCD_1in44.LCD_WIDTH-1, posx + 10), outline='WHITE', width=1)
    draw.text((70,posx), str(usage) + "%", fill = fontcolor)
    posx = posx + 10

   ##########component ram
   if 'ram' in cf["components"]:
    gpuram = int(re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True))))
    totalmem = round(psutil.virtual_memory()[0] / 1000 ** 2) + gpuram
    usagemem = round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)
    usageratemem = psutil.virtual_memory()[2]
    usagerategpuram = 100 / (totalmem + gpuram) * gpuram
    draw.text((0,posx), "RAM :", fill = cf["fontcolor"])
    width = (LCD_1in44.LCD_WIDTH - 1 - cf["boxmarginleft"]) /100 * usageratemem
    gpuwidth = (LCD_1in44.LCD_WIDTH - 1 - cf["boxmarginleft"]) /100 * usagerategpuram
    fontcolor = 'WHITE'
    if usageratemem >= 80: fillcolor = 'RED'
    elif usageratemem >= 60: fillcolor = 'YELLOW'
    else: fillcolor = 'GREEN'
    if fillcolor == 'YELLOW': fontcolor = 'GREY'
    draw.rectangle((cf["boxmarginleft"], posx) + (cf["boxmarginleft"] + width, posx + 10), fill=fillcolor, width=0)
    draw.rectangle((LCD_1in44.LCD_WIDTH-1-gpuwidth, posx) + (LCD_1in44.LCD_WIDTH-1, posx + 3), fill='RED', width=1)
    draw.rectangle((LCD_1in44.LCD_WIDTH-1-gpuwidth, posx + 4) + (LCD_1in44.LCD_WIDTH-1, posx + 6), fill='GREEN', width=1)
    draw.rectangle((LCD_1in44.LCD_WIDTH-1-gpuwidth, posx + 7) + (LCD_1in44.LCD_WIDTH-1, posx + 10), fill='BLUE', width=1)
    draw.rectangle((cf["boxmarginleft"], posx) + (LCD_1in44.LCD_WIDTH-1, posx + 10), outline='WHITE', width=1)
    draw.text((40,posx), str(usagemem) + "+" + str(gpuram) + "/" + str(totalmem) + "MB", fill = fontcolor)
    posx = posx + 10

   ##########component gpu
   if 'gpu' in cf["components"]:
    gpuram = re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True)))
    fontcolor = 'WHITE'
    draw.text((0,posx), "GPU: " + str(gpuram) + "MB", fill = fontcolor)
    posx = posx + 10

   ##########component temperatur
   if 'temperatur' in cf["components"]:
    tFile = open('/sys/class/thermal/thermal_zone0/temp')
    temp = int(format(int(float(tFile.read())/1000),"d"))
    draw.text((0,posx), "Temp:", fill = cf["fontcolor"])
    width = (LCD_1in44.LCD_WIDTH - 1 - cf["boxmarginleft"]) / (90 - 30) * (temp - 30)
    fontcolor = 'WHITE'
    if width < 0: width = 0
    if temp >= 70: fillcolor = 'RED'
    elif temp >= 60: fillcolor = 'YELLOW'
    else: fillcolor = 'GREEN'
    if fillcolor == 'YELLOW': fontcolor = 'GREY'
    draw.rectangle((cf["boxmarginleft"], posx) + (cf["boxmarginleft"] + width, posx + 10), fill=fillcolor, width=0)
    draw.rectangle((cf["boxmarginleft"], posx) + (LCD_1in44.LCD_WIDTH-1, posx + 10), outline='WHITE', width=1)
    draw.text((70,posx), str(temp) + '°C' , fontcolor)
    posx = posx + 10

   ##########component sd
   if 'sd' in cf["components"]:
    totalsd = psutil.disk_usage('/').total
    freesd = psutil.disk_usage('/').free
    usagesd = totalsd - freesd
    usagesdpercent = 100 / totalsd * usagesd

    if totalsd >= 17000000000: totalsd = 32
    elif totalsd >= 9000000000: totalsd = 16
    elif totalsd >= 5000000000: totalsd = 8
    elif totalsd >= 3000000000: totalsd = 4
    else: totalsd = 2

    usagesd = round(usagesd / (1024.0 ** 3),1)
    draw.text((0,posx), "SD  :", fill = cf["fontcolor"])
    width = (LCD_1in44.LCD_WIDTH - 1 - cf["boxmarginleft"]) /100 * usagesdpercent
    fontcolor = 'WHITE'
    if usagesdpercent >= 90: fillcolor = 'RED'
    elif usagesdpercent >= 70:
     fillcolor = 'YELLOW'
     fontcolor = 'GRAY'
    elif usagesdpercent < 50 and totalsd > 4: fillcolor = 'PURPLE'
    else: fillcolor = 'GREEN'
    draw.rectangle((cf["boxmarginleft"], posx) + (cf["boxmarginleft"] + width, posx + 10), fill=fillcolor, width=0)
    draw.rectangle((cf["boxmarginleft"], posx) + (LCD_1in44.LCD_WIDTH-1, posx + 10), outline='WHITE', width=1)
    draw.text((55,posx), str(usagesd) + "/" + str(totalsd) + "GB", fill = fontcolor)
    posx = posx + 10

   ##########component lastimage
   #Shows the latest file from a specified directory. If necessary, this is output as scrolling text.
   #I use this to see which filenames the latest image of the SD card has.
   if 'lastimage' in cf["components"]:
    try: marqueepos
    except: marqueepos = 0
    try: marqueewait
    except: marqueewait = 0
    if 'latest_file' not in locals():
     checkforlatestfile = str(cf["checkforlatestfile"]).replace("%HOSTNAME%", str(hostname).lower())
     list_of_files = glob.glob(checkforlatestfile)
    if len(list_of_files) == 0:
     draw.text((marqueepos ,posx), 'IMG :', fill = cf["fontcolor"])
     draw.text((marqueepos ,posx), '     missed', fill = 'RED')
    else:
     latest_file = max(list_of_files, key=os.path.getctime)
     latest_file_name = os.path.basename(latest_file)
     latest_file_name_text = 'IMG: ' + latest_file_name
     marqueewidth, marqueewidthheight = draw.textsize(latest_file_name_text)
     if marqueepos <= LCD_1in44.LCD_WIDTH - marqueewidth:
      marqueewait = marqueewait + 1
     else: marqueepos = marqueepos - 2
     if marqueewait > cf["scrollingtextwait"] / cf["imagerefresh"]:
      marqueepos = 0
      marqueewait = 0
     draw.text((marqueepos ,posx), latest_file_name_text, fill = cf["fontcolor"])
    posx = posx + 10

#####################################################promt picture to display
  if cf['rotate'] == 90: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_90),0,0)
  elif cf['rotate'] == 180: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_180),0,0)
  elif cf['rotate'] == 270: LCD.LCD_ShowImage(image.transpose(Image.ROTATE_270),0,0)
  else: LCD.LCD_ShowImage(image,0,0)

  time.sleep(int(cf["imagerefresh"]))

  try: lastpicturesave
  except: lastpicturesave = 0

  try:
   if time.time() >= lastpicturesave + int(cf["picturesaveintervall"]):
    saveimagedestination = str(cf["saveimagedestination"]).replace("%HOSTNAME%", str(hostname).lower())
    image.save(saveimagedestination,optimize=True)
    lastpicturesave = time.time()
  except:
   1+1

if __name__ == '__main__':
 main()
