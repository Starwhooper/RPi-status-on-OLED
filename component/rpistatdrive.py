def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import psutil
 import os
 import time

 global lastmessage

 image = Image.new("RGB", (lcd_width, len(cf["component_drive"]['drive'])*10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 drivenumber = 0
 
 try: lastmessage
 except: lastmessage = 0
 
 for drive in cf["component_drive"]['drive']:
  if os.path.isdir(drive):
   totalsd = psutil.disk_usage(drive).total
   freesd = psutil.disk_usage(drive).free
   usagesd = totalsd - freesd
   usagesdpercent = 100 / totalsd * usagesd
 
   usagesd = round(usagesd / (1024.0 ** 3),1)
   draw.text((0,drivenumber*10), "Drv" + str(drivenumber) + ':', fill = cf["fontcolor"])
   
   width = (lcd_width - 1 - cf["boxmarginleft"]) /100 * usagesdpercent
   fontcolor = cf['fontcolor']
   if usagesdpercent >= 90: fillcolor = 'RED'
   elif usagesdpercent >= 70:
    fillcolor = 'YELLOW'
    fontcolor = 'GRAY'
   else: fillcolor = 'GREEN'
   draw.rectangle((cf["boxmarginleft"], drivenumber*10) + (cf["boxmarginleft"] + width, drivenumber*10 + 10), fill=fillcolor, width=0)
   draw.rectangle((cf["boxmarginleft"], drivenumber*10) + (lcd_width-1, drivenumber*10 + 10), outline=cf['fontcolor'], width=1)
   draw.text((35,drivenumber*10), str(usagesd) + "/" + str(round(totalsd / 1024.0 ** 3,1)) + "GB", fill = fontcolor)
   drivenumber = drivenumber + 1
   if usagesdpercent >= 80:
    alert = '<b>' + drive + '</b>: <font color="' + fillcolor + '">' + str(round(usagesdpercent)) + '%</font> ' + str(usagesd) + ' GB used'
  else:
   print('folder ' + drive + ' not found')
  
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight, alert)
 
