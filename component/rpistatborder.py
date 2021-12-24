def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 
 image = Image.new("RGB", (lcd_width, 1), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 draw.rectangle((cf["boxmarginleft"], 0) + (lcd_width-1, 0 + 1), outline=cf['fontcolor'], width=1)
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 
