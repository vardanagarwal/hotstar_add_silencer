from mss import mss
import time
import os
from ultralytics import YOLO

import platform

if not os.path.exists('match'):
    os.mkdir('match')
if not os.path.exists('adds'):
    os.mkdir('adds')

def platform_setup():
    
    if system_platform == 'Windows':
        global IAudioEndpointVolume, AudioUtilities, cast, POINTER, CLSCTX_ALL
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    elif system_platform == 'Darwin':
        global subprocess
        import subprocess

    elif system_platform == 'Linux':
        global subprocess
        import subprocess
    else:
        print("Unsupported platform")
    
    return system_platform

def set_volume(volume):

    if system_platform == 'Windows':

        # Convert to scalar value between 0.0 and 1.0
        volume_level = volume / 100.0
        volume_control.SetMasterVolumeLevelScalar(volume_level, None)
    
    elif system_platform == 'Darwin':
        subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])
        
    elif system_platform == 'Linux':
        subprocess.run(["amixer", "-c", "0", "set", "Master", f"{volume}%"])

system_platform = platform.system()
platform_setup()
if platform.system() == 'Windows':
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))

model = YOLO('trained_model.pt')
# counter = [max(int(f.split('.')[0]) for f in os.listdir('adds')), max(int(f.split('.')[0]) for f in os.listdir('match')), max(int(f.split('.')[0]) for f in os.listdir('doubt'))]
counter = [0, 0, 0]
last = 'match'
volumes = [0, 70]
set_volume(volumes[1])
mss_obj = mss()
time.sleep(3)
while True:
    try:
        time.sleep(1)
        mss_obj.shot()
        # os.rename("monitor-1.png", f"images/{i}.png")
        results = model('monitor-1.png', imgsz=640)[0]
        probs = results.probs.data.cpu().numpy()
        classes = results.names.values()
        # write the image to its respective file
        # written = False
        for i, (cls, prob) in enumerate(zip(classes, probs)):
            if (i == 1 and prob >= 0.25) or (i == 0 and prob > 0.75):
                # print(f'---------{cls} {prob}---------')
                
                # written = True
                if cls != last:
                    os.rename("monitor-1.png", f"{cls}/{counter[i]}.png")
                    counter[i] += 1
                    set_volume(volumes[i])
                    last = cls
                break
            
    except Exception as e:
            print(e)
            # time.sleep(10)
            
