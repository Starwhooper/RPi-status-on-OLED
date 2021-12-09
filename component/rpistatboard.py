def output(cf,width):
 from PIL import Image
 from PIL import ImageDraw
 import re
 
 image = Image.new("RGB", (width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
# draw.text((0,0), 'Hello World' , fill = 'YELLOW')

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
 draw.text((0,0), "Main:" + piboardinformation, fill = cf["fontcolor"])
 
 width, height = image.size
 
 return (image,height)
 