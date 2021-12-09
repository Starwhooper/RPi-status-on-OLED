def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import re
 import subprocess
 import psutil
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 gpuram = int(re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True))))
 totalmem = round(psutil.virtual_memory()[0] / 1000 ** 2) + gpuram
 usagemem = round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)
 usageratemem = psutil.virtual_memory()[2]
 usagerategpuram = 100 / (totalmem + gpuram) * gpuram
 draw.text((0,0), "RAM :", fill = cf["fontcolor"])
 width = (lcd_width - 1 - cf["boxmarginleft"]) /100 * usageratemem
 gpuwidth = (lcd_width - 1 - cf["boxmarginleft"]) /100 * usagerategpuram
 fontcolor = cf['fontcolor']
 if usageratemem >= 80: fillcolor = 'RED'
 elif usageratemem >= 60: fillcolor = 'YELLOW'
 else: fillcolor = 'GREEN'
 if fillcolor == 'YELLOW': fontcolor = 'GREY'
 draw.rectangle((cf["boxmarginleft"], 0) + (cf["boxmarginleft"] + width, 0 + 10), fill=fillcolor, width=0)
 draw.rectangle((lcd_width-1-gpuwidth, 0) + (lcd_width-1, 0 + 3), fill='RED', width=1)
 draw.rectangle((lcd_width-1-gpuwidth, 0 + 4) + (lcd_width-1, 0 + 6), fill='GREEN', width=1)
 draw.rectangle((lcd_width-1-gpuwidth, 0 + 7) + (lcd_width-1, 0 + 10), fill='BLUE', width=1)
 draw.rectangle((cf["boxmarginleft"], 0) + (lcd_width-1, 0 + 10), outline=cf['fontcolor'], width=1)
 draw.text((40,0), str(usagemem) + "+" + str(gpuram) + "/" + str(totalmem) + "MB", fill = fontcolor)

 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 