from mss import mss
import time
import os

i = len(os.listdir("images_bkp"))
while True:
    time.sleep(10)
    mss().shot()
    os.rename("monitor-1.png", f"images/{i}.png")
    i += 1
    
