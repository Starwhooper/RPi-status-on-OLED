def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 #import ...
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 debianversionfile = open('/etc/debian_version','r')
 debianversion = debianversionfile.read()

 draw.text((0,0), "OS  :" + debianversion, fill = cf["fontcolor"])

 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 