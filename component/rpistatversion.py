def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
# import netifaces
# import time
 import os
 import re
 import subprocess

 image = Image.new("RGB", (lcd_width, 13), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 v = re.sub('[^0-9\-]+', '', str(subprocess.check_output('git -C ' + os.path.split(os.path.abspath(__file__))[0] + ' show -s --format=%cd --date=format:\'%y%m%d-%H%M\'', shell=True)))
 
 draw.text((0,0), "Scpt:" + v, fill = cf["fontcolor"])

 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
