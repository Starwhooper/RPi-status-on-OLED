def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import datetime
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 draw.text((0,0), "Date:" + datetime.date.today().strftime('%a')[:2] + datetime.date.today().strftime(', %d. %b.\'%y') , fill = cf["fontcolor"])
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 