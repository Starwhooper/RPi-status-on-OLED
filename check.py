#!/usr/bin/python3
import psutil    
import os
#import numpy
import time

gefunden = 0

for p in psutil.process_iter():
 if len(p.cmdline()) == 2:
  if p.cmdline()[0] == os.environ['_'] and p.cmdline()[1] == os.path.abspath(__file__):
   gefunden = gefunden + 1

if gefunden >= 2:
 print(gefunden)
 exit()
else:
 print('neu starten')
#    print(len(p.cmdline()))
#    print()
 
time.sleep(5)
