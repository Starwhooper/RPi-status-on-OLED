def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 #import ...
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 draw.text((0,0), 'Hello World' , fill = 'YELLOW')
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 