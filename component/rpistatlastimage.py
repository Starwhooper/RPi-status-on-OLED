def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import socket
 import glob
 import os

 global lastimagemarqueepos
 global lastimagemarqueewait
 
 hostname = str(socket.gethostname()).upper()
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 try: lastimagemarqueepos
 except: lastimagemarqueepos = 0
 try: lastimagemarqueewait
 except: lastimagemarqueewait = 0

 checkforlatestfile = str(cf["checkforlatestfile"]).replace("%HOSTNAME%", str(hostname).lower())
 list_of_files = glob.glob(checkforlatestfile)
 if len(list_of_files) == 0:
  draw.text((0 ,0), 'IMG :', fill = cf["fontcolor"])
  draw.text((0 ,0), '     missed', fill = 'RED')
 else:
  latest_file = max(list_of_files, key=os.path.getctime)
  latest_file_name = os.path.basename(latest_file)
  latest_file_name_text = 'IMG: ' + latest_file_name
  marqueewidth, marqueewidthheight = draw.textsize(latest_file_name_text)
  if lastimagemarqueepos <= lcd_width - marqueewidth:
   lastimagemarqueewait = lastimagemarqueewait + 1
  else: lastimagemarqueepos = lastimagemarqueepos - 2
  if lastimagemarqueewait > cf["scrollingtextwait"] / cf["imagerefresh"]:
   lastimagemarqueepos = 0
   lastimagemarqueewait = 0
  draw.text((lastimagemarqueepos ,0), latest_file_name_text, fill = cf["fontcolor"])
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
