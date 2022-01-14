def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import psutil
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 totalsd = psutil.disk_usage('/').total
 freesd = psutil.disk_usage('/').free
 usagesd = totalsd - freesd
 usagesdpercent = 100 / totalsd * usagesd

 if totalsd >= 17000000000: totalsd = 32
 elif totalsd >= 9000000000: totalsd = 16
 elif totalsd >= 5000000000: totalsd = 8
 elif totalsd >= 3000000000: totalsd = 4
 else: totalsd = 2

 usagesd = round(usagesd / (1024.0 ** 3),1)
 draw.text((0,0), "SD  :", fill = cf["fontcolor"])
 width = (lcd_width - 1 - cf["boxmarginleft"]) /100 * usagesdpercent
 fontcolor = cf['fontcolor']
 if usagesdpercent >= 90: fillcolor = 'RED'
 elif usagesdpercent >= 70:
  fillcolor = 'YELLOW'
  fontcolor = 'GRAY'
 elif usagesdpercent < 44 and totalsd > 4: fillcolor = 'PURPLE'
 else: fillcolor = 'GREEN'
 draw.rectangle((cf["boxmarginleft"], 0) + (cf["boxmarginleft"] + width, 0 + 10), fill=fillcolor, width=0)
 draw.rectangle((cf["boxmarginleft"], 0) + (lcd_width-1, 0 + 10), outline=cf['fontcolor'], width=1)
 draw.text((55,0), str(usagesd) + "/" + str(totalsd) + "GB", fill = fontcolor)
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 
