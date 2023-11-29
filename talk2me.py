#!/usr/bin/env python3
#
# script for motion activated sound track
# delivered to the matapedia's train station
# and art center.
#
# for auto-start on raspberry pi, add line in .bashrc :
# pgrep python
# if [ $? -ne 0 ]; then
#   echo "running at login"
#   python /path/to/script.py &
# fi
#
#
# voice and music by Naakita Feldman-Kiss and Rachel Nam
#
# code by Iko Lachapelle
# 2023-11-30


import os
import sys
import RPi.GPIO as GPIO
import time
from pygame import mixer

# init and PIN setup
button_en = 5 
button_fr = 6
sensor1 = 23
sensor2 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup([button_en, button_fr], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup([sensor1, sensor2], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(button_en, GPIO.FALLING)
GPIO.add_event_detect(button_fr, GPIO.FALLING)
GPIO.add_event_detect(sensor1, GPIO.RISING)
GPIO.add_event_detect(sensor2, GPIO.RISING)

mixer.init()
fr_track = '/home/gare/naakita/Matapedia_French.wav'
en_track = '/home/gare/naakita/Matapedia_English.wav'
maxIdle = 4 * 3600 # delay in hours before script restart
sensor_delay = 25 # delay (in seconds) between play() and reactivating sensors
lang = "en"
lastmove = time.time()
motion = 0

# script self restart function
def self_restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

# switch langage function
def fr_en(lg):
    if lg == "fr":
        mixer.music.load(fr_track)
        return "en"
    elif lg == "en":
        mixer.music.load(en_track)
        return "fr"

# main loop
try:
    while 1:
        # button interrupts
        if GPIO.event_detected(button_fr) or GPIO.event_detected(button_en):
            time.sleep(.100)
            if GPIO.input(button_fr) == GPIO.LOW:
                mixer.music.load(fr_track)
                mixer.music.play()
                lastmove = time.time()
            elif GPIO.input(button_en) == GPIO.LOW:
                mixer.music.load(en_track)
                mixer.music.play()
                lastmove = time.time()

        # motion sensors, keeps one movement in memory during track
        if (time.time() - lastmove) >= sensor_delay:
            if GPIO.event_detected(sensor1) or GPIO.event_detected(sensor2):
                time.sleep(1)
                if GPIO.input(sensor1) == GPIO.HIGH:
                    motion = 1
                elif GPIO.input(sensor2) == GPIO.HIGH:
                    motion = 1

        if motion:
            if not mixer.music.get_busy():
                lang = fr_en(lang)
                mixer.music.play()
                motion = 0
                lastmove = time.time()
        
        if (time.time() - lastmove) >= maxIdle:
            print("idle restart")
            self_restart()

        time.sleep(.200)


# end of script
finally:
    print("restarting ...")
    GPIO.cleanup()
    self_restart()
