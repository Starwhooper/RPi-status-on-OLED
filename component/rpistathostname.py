def output(cf,width):
 from PIL import Image
 from PIL import ImageDraw
 from PIL import ImageFont
 import socket
 import os

 #try: hostname
 #except: 
 hostname = str(socket.gethostname()).upper()

 image = Image.new("RGB", (width, 15), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 if os.path.isfile(cf["component_hostname"]["ttffont"]):
  ttffontheader = ImageFont.truetype(cf["component_hostname"]["ttffont"], 20)
  textwidth, textheight = draw.textsize(str(hostname), font=ttffontheader)
  draw.text( (((width-textwidth)/2) , 0), str(hostname), font=ttffontheader, fill = 'YELLOW')
 else:
  width, height = draw.textsize(str(hostname))
  imagehostname = Image.new("RGB", (width, height), "BLACK")
  drawimagehostname = ImageDraw.Draw(imagehostname)
  drawimagehostname.text((0,0), hostname , fill = 'YELLOW')
  factor=2
  imagehostname = imagehostname.resize((int(width*factor), int(height*factor)))
  image.paste(imagehostname,((int((LCD_1in44.LCD_WIDTH-(width*2))/2)),0))
 
 
 width, height = image.size
 
 return (image,height)
 