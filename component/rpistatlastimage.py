def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import socket
 import glob
 import os
 
 hostname = str(socket.gethostname()).upper()
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
# try: marqueepos
# except: marqueepos = 0
# try: marqueewait
# except: marqueewait = 0
# if 'latest_file' not in locals():
 checkforlatestfile = str(cf["checkforlatestfile"]).replace("%HOSTNAME%", str(hostname).lower())
 list_of_files = glob.glob(checkforlatestfile)
 if len(list_of_files) == 0:
  draw.text((0 ,0), 'IMG :', fill = cf["fontcolor"])
  draw.text((0 ,0), '     missed', fill = 'RED')
 else:
  latest_file = max(list_of_files, key=os.path.getctime)
  latest_file_name = os.path.basename(latest_file)
  latest_file_name_text = 'IMG: ' + latest_file_name
#  marqueewidth, marqueewidthheight = draw.textsize(latest_file_name_text)
#  if marqueepos <= LCD_1in44.LCD_WIDTH - marqueewidth:
#   marqueewait = marqueewait + 1
#  else: marqueepos = marqueepos - 2
#  if marqueewait > cf["scrollingtextwait"] / cf["imagerefresh"]:
#   marqueepos = 0
#   marqueewait = 0
  draw.text((0 ,0), latest_file_name_text, fill = cf["fontcolor"])

 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 