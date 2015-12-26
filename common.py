import os, win32gui, win32ui, win32api, win32con, win32print, sys, time

DEFAULT_DIRECTORY = 'test'

def get_active_window_dimensions():
    hwnd = win32gui.GetForegroundWindow()
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    w = r - l
    h = b - t

    return (l, t, w, h)

def capture_screen(directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)

    x, y, w, h = get_active_window_dimensions()

    # http://bytes.com/topic/python/answers/576924-win32ui-vs-wxpy-screen-capture-multi-monitor
    hwnd = win32gui.GetForegroundWindow()
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h),  mfcDC,  (0, 0),  win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC,  os.path.join(directory, filename))
    saveDC.DeleteDC()
    win32gui.DeleteObject(saveBitMap.GetHandle())

def countdown():
    for countdown in range(5, 0, -1):
        print "{}...".format(countdown)
        time.sleep(1)
    print "Go"