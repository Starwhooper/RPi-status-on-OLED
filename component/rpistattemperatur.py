def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 #import ...
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 tFile = open('/sys/class/thermal/thermal_zone0/temp')
 temp = int(format(int(float(tFile.read())/1000),"d"))
 draw.text((0,0), "Temp:", fill = cf["fontcolor"])
 width = (lcd_width - 1 - cf["boxmarginleft"]) / (90 - 30) * (temp - 30)
 fontcolor = cf['fontcolor']
 if width < 0: width = 0
 if temp >= 70: fillcolor = 'RED'
 elif temp >= 60: fillcolor = 'YELLOW'
 else: fillcolor = 'GREEN'
 if fillcolor == 'YELLOW': fontcolor = 'GREY'
 draw.rectangle((cf["boxmarginleft"], 0) + (cf["boxmarginleft"] + width, 0 + 10), fill=fillcolor, width=0)
 draw.rectangle((cf["boxmarginleft"], 0) + (lcd_width-1, 0 + 10), outline=cf['fontcolor'], width=1)
 draw.text((70,0), str(temp) + '°C' , fontcolor)

 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 