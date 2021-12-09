def output(cf,lcd_width):
 from PIL import Image
 from PIL import ImageDraw
 import time
 import psutil
 
 image = Image.new("RGB", (lcd_width, 10), cf["backgroundcolor"])
 draw = ImageDraw.Draw(image)
 
 def formatTimeAgo(seconds):
  if seconds < 60: return "%i seconds" % seconds
  elif seconds < 3600: return "%i minutes" % (seconds/float(60))
  elif seconds < (3600*24): return "%.1f hours" % (seconds/float(3600))
  elif seconds < (3600*24*7): return "%.1f days" % (seconds/float(3600*24))
  else: return "%.1f Weeks" % (seconds/float(3600*24*7))
 
 draw.text((0,0), "uptm:" + formatTimeAgo(time.time() - psutil.boot_time()) , fill = cf["fontcolor"])
 
 bannerwidth, bannerheight = image.size
 
 return (image,bannerheight)
 