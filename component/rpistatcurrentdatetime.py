def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import datetime
 import time
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 draw.rectangle((0, 9) + (lcd_width, 10), outline="DARKGRAY", width=1)
 draw.text((0,0), datetime.date.today().strftime('%a')[:2] + "," + datetime.date.today().strftime('%d.%b\'%y') + " " + time.strftime('%H:%M:%S', time.localtime()) , fill = cf["fontcolor"])
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
