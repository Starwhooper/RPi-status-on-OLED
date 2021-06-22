from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
import glob
#import http.client
import os
import re
import psutil
import requests
import RPi.GPIO as GPIO
import socket
import sys
import time
#import urllib
import subprocess

sys.path.append(r'/opt/LCD')
import LCD_1in44
import LCD_Config



########################################################init GPIO
GPIO.setmode(GPIO.BCM) 
#GPIO.cleanup()
KEY_UP_PIN     = 19 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY_DOWN_PIN   = 6                                            
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY_LEFT_PIN   = 26                                           
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY_RIGHT_PIN  = 5                                            
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY_PRESS_PIN  = 13                                           
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY1_PIN       = 16                                           
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY2_PIN       = 20                                           
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
KEY3_PIN       = 21                                           
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)

#def latest_image(path: Path, pattern: str = "/mnt/braavos/images/raspberry/devlog/_image/*.zip"):
#    files = path.glob(pattern)
#    return max(files, key=lambda x: x.stat().st_ctime)

def main():
 LCD = LCD_1in44.LCD()
 Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
 LCD.LCD_Init(Lcd_ScanDir)
 LCD.LCD_Clear()

######################################################Constant
 displaysizex = LCD_1in44.LCD_WIDTH
 displaysizey = LCD_1in44.LCD_HEIGHT
 pageids = [0,1,2,3,4]
 pagenames = ['Status','Service','...','Laptopgirl','Internetbild']
 imagerefresh = 0.2

######################################################first
 page = 0
 lastpiholversionintervall = 300
 lastpiholeversion = 0
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
  #hostname = hostname.upper()

#####################################################Which Page
#  if GPIO.input(KEY_UP_PIN) == 0:    page = 12
  if GPIO.input(KEY_LEFT_PIN) == 0:  page = page - 1
  if GPIO.input(KEY_RIGHT_PIN) == 0: page = page + 1
#  if GPIO.input(KEY_DOWN_PIN) == 0:  page = 6
  if page > pageids[-1]: page = pageids[0]
  if page < pageids[0]: page = pageids[-1]
  if lastpicturesave > 0:
   if time.time() >= lastpicturesave + picturesaveintervall: page = 0

#####################################################Bild generieren
  image = Image.new("RGB", (LCD.width, LCD.height), "BLACK")
  draw = ImageDraw.Draw(image)


#####################################################Bild generieren Page 0
  if page == 0: # Start
   posx = 0

   ###Hostname
   ttffont = "/usr/share/fonts/truetype/msttcorefonts/courbd.ttf"
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
    if os.system("ping -c 1 braavos.lan>/dev/null") == 0: pinglocalcolor = 'GREEN'
    else: pinglocalcolor = 'RED'
    if os.system("ping -c 1 google.de>/dev/null") == 0: pinginternetcolor = 'GREEN'
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
   
#   ###GPU RAM:
#   gpuram = re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True)))
#   fontcolor = 'WHITE'
#   draw.text((0,posx), "GPU: " + str(gpuram) + "MB", fill = fontcolor)
#   posx = posx + 10

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
   #print(latest_image(pathdirs))
   if 'latest_file' not in locals():
    list_of_files = glob.glob('/mnt/braavos/images/raspberry/' + hostname + '/_image/*.zip') # * means all if need specific format then *.csv
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

  if page == 1: # Service
   #####################################HOSTNAME = DEVLOP
   if hostname == 'DEVLOP': 
    draw.text((0,20), 'Entwicklungsumgebung', fill = 'WHITE')
   #####################################HOSTNAME = THEWALL (Pi-Hole)
   elif hostname == 'THEWALL': 
    if time.time() >= lastpiholeversion + lastpiholversionintervall:
     lastpiholeversion = time.time()
     piholeversion_current = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep Pi-hole | cut -d' ' -f6", shell=True)))
     piholeversion_latest = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep Pi-hole | cut -d' ' -f8", shell=True)))
     adminlteversion_current = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep AdminLTE | cut -d' ' -f6", shell=True)))
     adminlteversion_latest = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep AdminLTE | cut -d' ' -f8", shell=True)))
     ftlversion_current = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep FTL | cut -d' ' -f6", shell=True)))
     ftlversion_latest = re.sub('[^0-9.]+', '', str(subprocess.check_output("/usr/local/bin/pihole -v | grep FTL | cut -d' ' -f8", shell=True)))
    draw.text((0,0), 'DNS Versions', fill = 'WHITE')
    draw.text((0,10), "Pi-hole:", fill = 'WHITE')
    if piholeversion_current == piholeversion_latest: fontcolor = "WHITE"
    else: fontcolor = "RED"
    draw.text((0,20), str(piholeversion_current) + " of " + str(piholeversion_latest), fill = fontcolor)
    draw.text((0,30), "AdminLTE:", fill = 'WHITE')
    if adminlteversion_current == adminlteversion_latest: fontcolor = "WHITE"
    else: fontcolor = "RED"
    draw.text((0,40), str(adminlteversion_current) + " of " + str(adminlteversion_latest), fill = fontcolor)
    draw.text((0,50), "FTL:", fill = 'WHITE')
    if ftlversion_current == ftlversion_latest: fontcolor = "WHITE"
    else: fontcolor = "RED"
    draw.text((0,60), str(ftlversion_current) + " of " + str(ftlversion_latest), fill = fontcolor)
   #####################################HOSTNAME = PENTOS
   elif hostname == 'PENTOS':
    list_of_files_cam5 = glob.glob('/mnt/braavos/security/camera5/pictures/' + str(datetime.date.today().strftime('%Y-%m')) + '/' + str(datetime.date.today().strftime('%Y-%m-%d')) + '/' + str(datetime.date.today().strftime('%Y-%m-%d-%H')) + '/*.jpg')
    list_of_files_cam1 = glob.glob('/mnt/braavos/security/camera5/pictures/' + str(datetime.date.today().strftime('%Y-%m')) + '/' + str(datetime.date.today().strftime('%Y-%m-%d')) + '/' + str(datetime.date.today().strftime('%Y-%m-%d-%H')) + '/*.jpg')
    #list_of_files_cam1 = glob.glob('/mnt/braavos/security/camera1/pictures/' + str(datetime.date.today().strftime('%Y-%m')) + '/' + str(datetime.date.today().strftime('%Y-%m-%d')) + '/*.jpg')
    if len(list_of_files_cam5) >= 1:
     latest_file = max(list_of_files_cam5, key=os.path.getctime)
     my_file = Path(latest_file)
     if my_file.is_file(): 
      camerapic = Image.open(latest_file)
      camerapic = camerapic.resize((displaysizex,int(displaysizey/16*9)))
      image.paste(camerapic,(0,13,displaysizex,int(displaysizey/16*9)+13))
    elif len(list_of_files_cam1) >= 1:
     latest_file = max(list_of_files_cam1, key=os.path.getctime)
     my_file = Path(latest_file)
     if my_file.is_file(): 
      camerapic = Image.open(latest_file)
      camerapic = camerapic.resize((displaysizex,int(displaysizey/16*9)))
      image.paste(camerapic,(0,13,displaysizex,int(displaysizey/16*9)+13))
    else: draw.text((0,10), 'no image found', "YELLOW")
    draw.text((0,1), 'Überwachungskamera', fill = 'WHITE')
    thiemopositionfile = "/opt/positioncheck/thiemo.info"
    if os.path.isfile(thiemopositionfile):
     position = open(thiemopositionfile, "r").read()
    else: position = "unknown"
    draw.text((0,(displaysizey/16*9)+13), 'Thiemo is at ' + position, fill = 'WHITE')
   else: draw.text((0,20), 'nichts besonderes', fill = 'WHITE')

  if page == 2: # ...
   draw.text((0,1), '...', fill = 'WHITE')

  if page == 3: # Laptopgirl
   wallpaper = '/mnt/braavos/images/raspberry/laptopgirl.jpg'
   my_file = Path(wallpaper)
   if my_file.is_file(): 
    imagewallpaper = Image.open(wallpaper)
    image.paste(imagewallpaper)

  if page == 4: # Internetimage
   wallpaper = 'https://64.media.tumblr.com/b24c19504b3832365d6fee08b48bda01/tumblr_nkxfj0hWNA1sa5af1o1_400.png'
   imagewallpaper = Image.open(requests.get(wallpaper, stream=True).raw)
   imagewallpaper = imagewallpaper.resize((displaysizex,displaysizey))
   image.paste(imagewallpaper)


##############Allgemein
  i=0
  while i <= displaysizex:
   draw.point((i,displaysizey-1), fill= 'GRAY')
   i = (i + 10)
  i=0
  while i <= displaysizey:
   draw.point((displaysizex-1,i), fill= 'GRAY')
   i = (i + 10)
  draw.text((0,118), '<-', fill = 'WHITE')
  draw.text(((displaysizex-draw.textsize(str(pagenames[page]))[0])/2,118), str(pagenames[page]), fill = 'WHITE')
  draw.text((115,118), '->', fill = 'WHITE')


#####################################################Bild ausgeben



  image = image.resize((displaysizex, displaysizey))
  LCD.LCD_ShowImage(image.transpose(Image.ROTATE_90),0,0)
  time.sleep(imagerefresh)

  
  if time.time() >= lastpicturesave + picturesaveintervall: #Saves image all x seconds
   image.save(r'/mnt/braavos/images/raspberry/status_' + str(socket.gethostname()) + '.png',optimize=True)
   lastpicturesave = time.time()


if __name__ == '__main__':
 main()
