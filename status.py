from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
import glob
import http.client
import os
import psutil
import RPi.GPIO as GPIO
import socket
import sys
import time
import urllib
import subprocess

sys.path.append(r'/opt/LCD')
import LCD_1in44
import LCD_Config

KEY_UP_PIN     = 19 
KEY_DOWN_PIN   = 6
KEY_LEFT_PIN   = 26
KEY_RIGHT_PIN  = 5
KEY_PRESS_PIN  = 13
KEY1_PIN       = 16
KEY2_PIN       = 20
KEY3_PIN       = 21

#init GPIO
GPIO.setmode(GPIO.BCM) 
#GPIO.cleanup()
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

today = datetime.date.today()
fontcolornormal = 'WHITE'
fontcolorwarning = 'YELLOW'
fontcoloralert = 'RED'
zeilenhoehe = 9
image6 = '/mnt/braavos/images/raspberry/laptopgirl.jpg'
image3 = '/mnt/braavos/security/camera2/pictures/' + today.strftime('%Y-%m-%d') + '/*.jpg'
#lastpicturesave = time.time()
lastpicturesave = 0
displaysizex = 128
displaysizey = 128
stayonpagedefault = 10
stayonpage = stayonpagedefault
hostname = str(socket.gethostname())

def get_whereisthiemo():
 command = open("/opt/positioncheck/thiemo.info", "r").read()
# command = str(socket.gethostname())
 output = str(command)
 fontcolor = fontcolornormal
 if output == 'outside': fontcolor = fontcoloralert
 return (output,fontcolor)

def get_hostname():
 command = str(socket.gethostname())
 output = str(command)
 fontcolor = fontcolornormal
 if len(output) < 3: fontcolor = fontcoloralert
 return (output,fontcolor)

def get_ip():
 command = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
 output = str(command)
 fontcolor = fontcolornormal
 return (output,fontcolor)

def get_date():
 now = datetime.date.today()
 output = now.strftime('%a, %-d. %b.\'%y')
 output = str(output)
 fontcolor = fontcolornormal
 if int(now.strftime('%Y')) < 2020: fontcolor = fontcoloralert
 return (output,fontcolor)

def get_time():
 now = datetime.datetime.today()
 output = now.strftime('%-H:%M:%S')
 output = str(output)
 fontcolor = fontcolornormal
 return (output,fontcolor)

def get_internetconnection():
 conn = http.client.HTTPConnection("172.217.19.78", timeout=3)
 try:
  conn.request("HEAD", "/")
  conn.close()
  output = 'aviable'
  fontcolor = fontcolornormal
 except Exception as e:
  output = 'unaviable'
  fontcolor = fontcoloralert
 return (output,fontcolor)

def get_nasconnection():
 nas = 'braavos.lan'
 response = os.system("ping -c 1 " + nas + ">/dev/null 2>&1")
 if response == 0:
  output = nas + ' aviable'
  fontcolor = fontcolornormal
 else:
  output = nas + ' unaviable'
  fontcolor = fontcoloralert
 return(output, fontcolor)

def get_piboard():
 fobj = open("/sys/firmware/devicetree/base/model")
 output = ''
 for line in fobj:
    output = output + line.rstrip()
 fobj.close()
 output = output.replace("Raspberry Pi", "RPi")
 output = output.replace(" Model ", "")
 output = output.replace("Rev ", "")
 output = output[:10]
 ram = round(psutil.virtual_memory()[0] / (1024.0 ** 3))
 output = str(output) + ' ' + str(ram) + 'GB'
 fontcolor = fontcolornormal
 return(output, fontcolor)

#def get_cpuinfo():
# tFile = open('/sys/class/thermal/thermal_zone0/temp')
# tempoutput = format(int(float(tFile.read())/1000),"d")
# percentoutput = psutil.cpu_percent()
# fontcolor = fontcolornormal
# if int(tempoutput) >= 60: fontcolor = fontcolorwarning
# if int(percentoutput) >= 60: fontcolor = fontcolorwarning
# if int(tempoutput) >= 70: fontcolor = fontcoloralert
# if int(percentoutput) >= 80: fontcolor = fontcoloralert
# percentoutput = str(percentoutput)
# if len(percentoutput) == 3: percentoutput = ' ' + percentoutput
# output = percentoutput + '% ' + str(tempoutput) + '\'C'
# return(output, fontcolor)

def get_cpuusage():
# tFile = open('/sys/class/thermal/thermal_zone0/temp')
# tempoutput = format(int(float(tFile.read())/1000),"d")
 percentoutput = psutil.cpu_percent()
 fontcolor = fontcolornormal
# if int(tempoutput) >= 60: fontcolor = fontcolorwarning
 if int(percentoutput) >= 60: fontcolor = fontcolorwarning
# if int(tempoutput) >= 70: fontcolor = fontcoloralert
 if int(percentoutput) >= 80: fontcolor = fontcoloralert
 percentoutput = str(percentoutput)
 if len(percentoutput) == 3: percentoutput = ' ' + percentoutput
# output = percentoutput + '% ' + str(tempoutput) + '\'C'
 output = percentoutput + '%'
 return(output, fontcolor)

def get_cputemp():
 tFile = open('/sys/class/thermal/thermal_zone0/temp')
 tempoutput = format(int(float(tFile.read())/1000),"d")
# percentoutput = psutil.cpu_percent()
 fontcolor = fontcolornormal
 if int(tempoutput) >= 60: fontcolor = fontcolorwarning
# if int(percentoutput) >= 60: fontcolor = fontcolorwarning
 if int(tempoutput) >= 70: fontcolor = fontcoloralert
# if int(percentoutput) >= 80: fontcolor = fontcoloralert
# percentoutput = str(percentoutput)
# if len(percentoutput) == 3: percentoutput = ' ' + percentoutput
 output = str(tempoutput) + '\'C'
 return(output, fontcolor)

def get_sdinfo():
 obj_Disk = psutil.disk_usage('/')
 usedsd = round(obj_Disk.used / (1024.0 ** 3),2)
 usepercentsd = (obj_Disk.percent)
 fontcolor = fontcolornormal
 if usepercentsd >= 80: fontcolor = fontcolorwarning
 if usepercentsd >= 90: fontcolor = fontcoloralert
 output = str(usedsd) + 'GB (' + str(usepercentsd) + '%)'
 return(output, fontcolor)

def get_raminfo():
 output = str(psutil.virtual_memory()[2]) + '%'
 fontcolor = fontcolornormal
 if psutil.virtual_memory()[2] >= 80: fontcolor = fontcolorwarning
 if psutil.virtual_memory()[2] >= 90: fontcolor = fontcoloralert
 return(output, fontcolor)

def get_piholedbsize():
 dbsize = round(os.path.getsize("/etc/pihole/pihole-FTL.db") / (1024.0 ** 3),2)
 output = str(dbsize)
 fontcolor = fontcolornormal
 if dbsize >= 1.5: fontcolor = fontcolorwarning
 if dbsize >= 2: fontcolor = fontcoloralert
 #output = output / (1024.0 ** 3)
 return(output, fontcolor)
 
def main():
 LCD = LCD_1in44.LCD()
 Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
 LCD.LCD_Init(Lcd_ScanDir)
 
 LCD.LCD_Clear()
 
 if len(sys.argv) > 1:
  if str(sys.argv[1]) == 'test': 
   runmode = 'test'
  if str(sys.argv[1]) == 'run': 
   runmode = 'run'
  if str(sys.argv[1]) == 'onetime': 
   runmode = 'onetime'
 else:
  runmode = 'none'
 
 status = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
 
 defaultpage = 12
 page = defaultpage
 pagesettime = 0
 global lastpicturesave
 global stayonpage
 
 while True:
   
  image = Image.new("RGB", (LCD.width, LCD.height), "BLACK")
  draw = ImageDraw.Draw(image)
  
  if GPIO.input(KEY_UP_PIN) == 0:    page = 12
  if GPIO.input(KEY_LEFT_PIN) == 0:  page = 9
  if GPIO.input(KEY_RIGHT_PIN) == 0: page = 3
  if GPIO.input(KEY_DOWN_PIN) == 0:  page = 6
  if page == defaultpage: pagesettime = 0
  if page != defaultpage: 
   if pagesettime == 0: pagesettime = time.time()
   if pagesettime + stayonpage < time.time(): 
    stayonpage = stayonpagedefault
    page = defaultpage
    pagesettime = 0
  
  if page == 3:
   list_of_files = glob.glob(image3)
   if len(list_of_files) >= 1:
    latest_file = max(list_of_files, key=os.path.getctime)
    my_file = Path(latest_file)
    if my_file.is_file(): 
     stayonpage = 30
     image = Image.open(latest_file)
   #else:
#     draw.text((  0, 0), latest_file, "YELLOW")     
   draw.text((  0, 0), 'no image found', "YELLOW")
   draw.text((  0, 10), image3, "YELLOW")
	
  if page == 6:
   my_file = Path(image6)
   if my_file.is_file(): 
    image = Image.open('/mnt/braavos/images/raspberry/laptopgirl.jpg')
   else:
    draw.text((  20, 20), 'Page 6', "ORANGE")  

  if page == 9:
   draw.text((  20, 20), 'Page 9', "PURPLE")  
   
  if page == 12:
   ################BUTTONANZEIGE###############
   status[12] = [100, 100, '', "GREEN"]
   if GPIO.input(KEY_UP_PIN) == 0:    status[12] = [119, 119, '^', "GREEN"]
   if GPIO.input(KEY_LEFT_PIN) == 0:  status[12] = [119, 119, '<', "GREEN"]
   if GPIO.input(KEY_RIGHT_PIN) == 0: status[12] = [119, 119, '>', "GREEN"]
   if GPIO.input(KEY_DOWN_PIN) == 0:  status[12] = [119, 119, 'v', "GREEN"]
   if GPIO.input(KEY_PRESS_PIN) == 0: status[12] = [119, 119, 'J', "GREEN"]
   if GPIO.input(KEY1_PIN) == 0:      status[12] = [119, 119, '1', "GREEN"]
   if GPIO.input(KEY2_PIN) == 0:      status[12] = [119, 119, '2', "GREEN"]
   if GPIO.input(KEY3_PIN) == 0:      status[12] = [119, 119, '3', "GREEN"]
   
   posx = 1
   posy = 0
   i = 1
  
  
   ##########HOSTNAME
   values = get_hostname()
   text = 'HST:' + values[0]
   color = values[1]
   status[i] = [posx, posy, text, color]
   i = i + 1
   posy = posy + zeilenhoehe
   
   ##########IP 
   values = get_ip()
   text = 'IP :' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########Datum
   values = get_date()
   text = 'DAT:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########Uhrzeit
   values = get_time()
   text = 'TME:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########Internetverbindung
   values = get_internetconnection()
   text = 'INT:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########NAS erreichbar
   values = get_nasconnection()
   text = 'NAS:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########Platinentyp
   values = get_piboard()
   text = 'BRD:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1
   
   ##########CPU Info
   values = get_cpuusage()
   text = 'CPU:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1

   ##########CPU Info
   values = get_cputemp()
   text = 'CPU:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1

#   ##########CPU Info
#   values = get_cpuinfo()
#   text = 'CPU:' + values[0]
#   color = values[1]
#   posy = posy + zeilenhoehe
#   status[i] = [posx, posy, text, color]
#   i = i + 1
   
   ##########SD Info
   values = get_sdinfo()
   text = 'SD :' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1

   ##########RAM Info
   values = get_raminfo()
   text = 'RAM:' + values[0]
   color = values[1]
   posy = posy + zeilenhoehe
   status[i] = [posx, posy, text, color]
   i = i + 1

   ##########PiHole DB Size
   if hostname == 'thewall':
    values = get_piholedbsize()
    text = 'PDB:' + values[0] + 'GB'
    color = values[1]
    posy = posy + zeilenhoehe
    status[i] = [posx, posy, text, color]
    i = i + 1
   
   ##########Where is Thiemo
   if hostname == 'pentos':
    values = get_whereisthiemo()
    text = 'POS:Thiemo is ' + values[0]
    color = values[1]
    posy = posy + zeilenhoehe
    status[i] = [posx, posy, text, color]
    i = i + 1
   
   ###########CREATE IMAGE
   for i in status:
    if isinstance(i, list):
     if os.path.isfile('/home/pi/.fonts/courier-new.ttf'):
      if 'HST:' in i[2]:
       i[2] = i[2][4:]
       i[2] = i[2].upper()
       fnt = ImageFont.truetype('/home/pi/.fonts/courier-new.ttf', 20)
       width,height = draw.textsize(str(i[2]), font=fnt)
       draw.text( (((displaysizex-width)/2) , i[1]), str(i[2]), font=fnt, fill = 'YELLOW')
      else:
       fnt = ImageFont.load_default()
       draw.text(( i[0], i[1]), str(i[2]), font=fnt, fill = i[3])
     else:
      draw.text(( i[0], i[1]), str(i[2]), fill = i[3])
  
  image = image.resize((displaysizex, displaysizey))
  LCD.LCD_ShowImage(image.transpose(Image.ROTATE_180),0,0)
  
  #if runmode == 'test': 
  
  if time.time() >= lastpicturesave + 3600: #Saves image all x seconds
   image.save(r'/mnt/braavos/images/raspberry/status_' + str(socket.gethostname()) + '.png',optimize=True)
   lastpicturesave = time.time()
  #if runmode != "run": 
  # break
 
  time.sleep(0.2)


if __name__ == '__main__':
    main()
