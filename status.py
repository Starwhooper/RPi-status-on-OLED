#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# checkout: https://github.com/Starwhooper/RPi-status-on-OLED

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

sys.path.append('/opt/LCD')
import LCD_1in44
import LCD_Config

########################################################import config.json

if os.path.isfile('config.json'):
 with open('config.json','r') as file:
  cf = json.loads(file.read())
else: sys.exit("No config files found, please rename file config.json.example to config.json and chnage the content to you need")


########################################################init GPIO
GPIO.setmode(GPIO.BCM) 

KEY_PRESS_PIN  = 13
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
 LCD = LCD_1in44.LCD()
 Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
 LCD.LCD_Init(Lcd_ScanDir)
 LCD.LCD_Clear()

######################################################Constant
 displaysizex = LCD_1in44.LCD_WIDTH
 displaysizey = LCD_1in44.LCD_HEIGHT
 imagerefresh = 0.2
 ttffont = cf["ttffont"]
 localpingdestination = cf["localpingdestination"]
 remotepingdestination = cf["remotepingdestination"]
 checkforlatestfile = cf["checkforlatestfile"]
 saveimagedestination = cf["saveimagedestination"]

######################################################first
 lastpicturesave = 999999999
 picturesaveintervall = 3600
 lastping = 0
 pingintervall = 300
 pinglocalcolor = 'YELLOW'
 pinginternetcolor = 'YELLOW'
 borderstartsatx = 33 - 4
 marqueepos = 0
 marqueewait = 0

 while True:
####################################################Prüfungen
  if 'hostname' in locals():
   hostname = hostname
  else:
   hostname = str(socket.gethostname()).upper()
  if 'ip' in locals():
   ip = ip
  else:
   ip = str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

#####################################################Bild generieren
  image = Image.new("RGB", (LCD.width, LCD.height), "BLACK")
  draw = ImageDraw.Draw(image)

  if GPIO.input(KEY_PRESS_PIN) == 0:
   draw.text(( 0 , 0), "Hi :-)", fill = 'RED')

#####################################################Bild generieren

  posx = 0

  ###Hostname
  if os.path.isfile(ttffont):
   ttffontheader = ImageFont.truetype(ttffont, 20)
   width, height = draw.textsize(str(hostname), font=ttffontheader)
   draw.text( (((displaysizex-width)/2) , 0), str(hostname), font=ttffontheader, fill = 'YELLOW')
  else:
   width, height = draw.textsize(str(hostname))
   imagehostname = Image.new("RGB", (width, height), "BLACK")
   drawimagehostname = ImageDraw.Draw(imagehostname)
   drawimagehostname.text((0,0), hostname , fill = 'YELLOW')
   factor=2
   imagehostname = imagehostname.resize((int(width*factor), int(height*factor)))
   image.paste(imagehostname,((int((displaysizex-(width*2))/2)),0))
  posx = posx + 20
  
  ###Date
  draw.text((0,posx), "Date:" + datetime.date.today().strftime('%a')[:2] + datetime.date.today().strftime(', %d. %b.\'%y') , fill = 'WHITE')
  posx = posx + 10
  
  ###IP
  draw.text((0,posx), "IP  :" + ip , fill = 'WHITE')
  posx = posx + 10
  
  ###Ping
  pinglocal = pinginternet = "offline"
  if time.time() >= lastping + pingintervall: #Ping systems all x seconds
   if os.system("ping -c 1 " + localpingdestination + ">/dev/null") == 0: pinglocalcolor = 'GREEN'
   else: pinglocalcolor = 'RED'
   if os.system("ping -c 1 " + remotepingdestination + ">/dev/null") == 0: pinginternetcolor = 'GREEN'
   else: pinginternetcolor = 'RED'
   lastping = int(time.time())
  draw.rectangle((0, posx + 11) + (int( displaysizex / pingintervall * (int(time.time()) - lastping)), posx + 12), fill="GREEN", width=1)
  draw.text((0,posx), "Ping:     ,", fill = 'WHITE')
  draw.text((0,posx), "     LOCAL", fill = pinglocalcolor)
  draw.text((0,posx), "           REMOTE", fill = pinginternetcolor)
  posx = posx + 13

  ###PI Board
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
  draw.text((0,posx), "Main:" + piboardinformation, fill = 'WHITE')
  posx = posx + 10

  ###CPU Usage
  usage = int(float(psutil.cpu_percent()))
  draw.text((0,posx), "CPU :", fill = 'WHITE')
  width = (displaysizex - 1 - borderstartsatx) /100 * usage
  fontcolor = 'WHITE'
  if usage >= 80: fillcolor = 'RED'
  elif usage >= 60: fillcolor = 'YELLOW'
  else: fillcolor = 'GREEN'
  if fillcolor == 'YELLOW': fontcolor = 'GREY'
  draw.rectangle((borderstartsatx, posx) + (borderstartsatx + width, posx + 10), fill=fillcolor, width=0)
  draw.rectangle((borderstartsatx, posx) + (displaysizex-1, posx + 10), outline='WHITE', width=1)
  draw.text((70,posx), str(usage) + "%", fill = fontcolor)
  posx = posx + 10

  ###RAM Usage
  gpuram = int(re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True))))
  totalmem = round(psutil.virtual_memory()[0] / 1000 ** 2) + gpuram
  usagemem = round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)
  usageratemem = psutil.virtual_memory()[2]
  usagerategpuram = 100 / (totalmem + gpuram) * gpuram
  draw.text((0,posx), "RAM :", fill = 'WHITE')
  width = (displaysizex - 1 - borderstartsatx) /100 * usageratemem
  gpuwidth = (displaysizex - 1 - borderstartsatx) /100 * usagerategpuram
  fontcolor = 'WHITE'
  if usageratemem >= 80: fillcolor = 'RED'
  elif usageratemem >= 60: fillcolor = 'YELLOW'
  else: fillcolor = 'GREEN'
  if fillcolor == 'YELLOW': fontcolor = 'GREY'
  draw.rectangle((borderstartsatx, posx) + (borderstartsatx + width, posx + 10), fill=fillcolor, width=0)
  draw.rectangle((displaysizex-1-gpuwidth, posx) + (displaysizex-1, posx + 3), fill='RED', width=1)
  draw.rectangle((displaysizex-1-gpuwidth, posx + 4) + (displaysizex-1, posx + 6), fill='GREEN', width=1)
  draw.rectangle((displaysizex-1-gpuwidth, posx + 7) + (displaysizex-1, posx + 10), fill='BLUE', width=1)
  draw.rectangle((borderstartsatx, posx) + (displaysizex-1, posx + 10), outline='WHITE', width=1)
  draw.text((40,posx), str(usagemem) + "+" + str(gpuram) + "/" + str(totalmem) + "MB", fill = fontcolor)
  posx = posx + 10
  
  ###GPU RAM:
  gpuram = re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True)))
  fontcolor = 'WHITE'
  draw.text((0,posx), "GPU: " + str(gpuram) + "MB", fill = fontcolor)
  posx = posx + 10

  ###Temp
  tFile = open('/sys/class/thermal/thermal_zone0/temp')
  temp = int(format(int(float(tFile.read())/1000),"d"))
  draw.text((0,posx), "Temp:", fill = 'WHITE')
  width = (displaysizex - 1 - borderstartsatx) / (90 - 30) * (temp - 30)
  fontcolor = 'WHITE'
  if width < 0: width = 0
  if temp >= 70: fillcolor = 'RED'
  elif temp >= 60: fillcolor = 'YELLOW'
  else: fillcolor = 'GREEN'
  if fillcolor == 'YELLOW': fontcolor = 'GREY'
  draw.rectangle((borderstartsatx, posx) + (borderstartsatx + width, posx + 10), fill=fillcolor, width=0)
  draw.rectangle((borderstartsatx, posx) + (displaysizex-1, posx + 10), outline='WHITE', width=1)
  draw.text((70,posx), str(temp) + '°C' , fontcolor)
  posx = posx + 10

  ###SD Usage
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
  draw.text((0,posx), "SD  :", fill = 'WHITE')
  width = (displaysizex - 1 - borderstartsatx) /100 * usagesdpercent
  fontcolor = 'WHITE'
  if usagesdpercent >= 90: fillcolor = 'RED'
  elif usagesdpercent >= 70:
   fillcolor = 'YELLOW'
   fontcolor = 'GRAY'
  elif usagesdpercent < 50 and totalsd > 4: fillcolor = 'PURPLE'
  else: fillcolor = 'GREEN'
  draw.rectangle((borderstartsatx, posx) + (borderstartsatx + width, posx + 10), fill=fillcolor, width=0)
  draw.rectangle((borderstartsatx, posx) + (displaysizex-1, posx + 10), outline='WHITE', width=1)
  draw.text((55,posx), str(usagesd) + "/" + str(totalsd) + "GB", fill = fontcolor)
  posx = posx + 10
  
  ###Last Image
  if 'latest_file' not in locals():
   list_of_files = glob.glob(checkforlatestfile)
  if len(list_of_files) == 0:
   draw.text((marqueepos ,posx), 'IMG :', fill = fontcolor) 
   draw.text((marqueepos ,posx), '     missed', fill = 'RED') 
  else:
   latest_file = max(list_of_files, key=os.path.getctime)
   latest_file_name = os.path.basename(latest_file)
   latest_file_name_text = 'IMG: ' + latest_file_name
   marqueewidth, marqueewidthheight = draw.textsize(latest_file_name_text)
   if marqueepos <= displaysizex - marqueewidth: 
    marqueewait = marqueewait + 1
   else: marqueepos = marqueepos - 2
   if marqueewait > 5 / imagerefresh: 
    marqueepos = 0
    marqueewait = 0
   draw.text((marqueepos ,posx), latest_file_name_text, fill = fontcolor) 
  posx = posx + 10

#####################################################Bild ausgeben
  image = image.resize((displaysizex, displaysizey))
  LCD.LCD_ShowImage(image.transpose(Image.ROTATE_90),0,0)
  time.sleep(imagerefresh)

  
  if time.time() >= lastpicturesave + picturesaveintervall: #Saves image all x seconds
   image.save(saveimagedestination,optimize=True)
   lastpicturesave = time.time()


if __name__ == '__main__':
 main()
