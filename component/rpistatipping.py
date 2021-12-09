def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import netifaces
 import time
 import os
 
 image = Image.new("RGB", (lcd_width, 13), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 try: ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
 except: ip = 'noip'

 
# try: lastping
# except: lastping = 0
 pinglocal = pinginternet = "offline"
 if len(cf["localpingdestination"]) >= 1: localpingdestination = cf["localpingdestination"]
 else: localpingdestination = ip[0:ip.rfind('.')] + '.1'
 #if time.time() >= lastping + cf["pingintervall"]: #Ping systems all x seconds
 if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinglocalcolor = 'GREEN'
 else: pinglocalcolor = 'RED'
 if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinginternetcolor = 'GREEN'
 else: pinginternetcolor = 'RED'
 #lastping = int(time.time())
 draw.text((0,0), "IP  :" + ip , fill = cf["fontcolor"])
 #draw.rectangle((0, 0 + 11) + (int( lcd_width / cf["pingintervall"] * (int(time.time()) - lastping)), 0 + 12), fill="GREEN", width=1)
 draw.text((0,0), "  L", fill = pinglocalcolor)
 draw.text((0,0), "   R", fill = pinginternetcolor)

 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 