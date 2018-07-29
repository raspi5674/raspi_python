from picamera import PiCamera
from time import sleep

# Resolution code: 
#camera = PiCamera(resolution=(3280,2464))
camera = PiCamera()
camera.rotation = 90

camera.resolution = (3280,2464)
sleep(5)
camera.capture('/home/pi/test3.jpg')

camera.resolution = (800, 600)
sleep(5)
camera.capture('/home/pi/test4.jpg')

