def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import psutil
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 usage = int(float(psutil.cpu_percent()))
 draw.text((0,0), "CPU :", fill = cf["fontcolor"])
 width = (lcd_width - 1 - cf["boxmarginleft"] ) /100 * usage
 fontcolor = cf['fontcolor']
 if usage >= 80: fillcolor = 'RED'
 elif usage >= 60: fillcolor = 'YELLOW'
 else: fillcolor = 'GREEN'
 if fillcolor == 'YELLOW': fontcolor = 'GREY'
 draw.rectangle((cf["boxmarginleft"], 0) + (cf["boxmarginleft"] + width, 0 + 10), fill=fillcolor, width=0)
 draw.rectangle((cf["boxmarginleft"], 0) + (lcd_width-1, 0 + 10), outline=cf['fontcolor'], width=1)
 draw.text((70,0), str(usage) + "%", fill = fontcolor)
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 