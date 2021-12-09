def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import time
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 draw.text((0,0), "Time:" + time.strftime('%H:%M:%S', time.localtime()) , fill = cf["fontcolor"])
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 