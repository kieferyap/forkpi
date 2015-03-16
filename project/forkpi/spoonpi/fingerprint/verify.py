
import FPS, sys

if __name__ == '__main__':
    fps = FPS.FPS_GT511C3(device_name='/dev/ttyAMA0',baud=9600,timeout=2) #settings for raspberry pi GPIO
    fps.Open()
    fps.SetLED(True)
    
    print 'Press finger to verify'
    while not fps.IsPressFinger():
        FPS.delay(1)

    if fps.CaptureFinger(False):
        print 'remove finger'
        id = fps.Identify1_N()
        if id < 200:
            print 'Match with id', id
        else:
            print 'No match found'
    else:
        print 'Failed to capture finger'
