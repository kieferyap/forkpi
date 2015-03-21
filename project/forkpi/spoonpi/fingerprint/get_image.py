import FPS, sys

def GetImage(fps):
    ret = bytes()
    if fps.GetImage():
        response = fps._lastResponse.RawBytes[16:]
        print(fps.serializeToSend(response))
        print('Size %s' % len(response))
        ret = bytes(response)
    FPS.delay(0.1)
    return ret

if __name__ == '__main__':
    fps = FPS.FPS_GT511C3(device_name='/dev/ttyAMA0',baud=9600,timeout=2) #settings for raspberry pi GPIO
    fps.Open()
    fps.SetLED(True)
    
    print('Press finger to verify')
    while not fps.IsPressFinger():
        FPS.delay(1)

    if fps.CaptureFinger(True):
        print('remove finger')
        GetImage(fps)
        GetImage(fps)
        GetImage(fps)
    else:
        print('Failed to capture finger')

    fps.SetLED(False)