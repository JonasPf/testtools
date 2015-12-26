"""Replay recorded mouse and keyboard events

Usage:
  replay.py <directory>

Options:
  -h --help    show this
"""

import sys, json, time, datetime
import docopt
from common import *
import pyHook

INPUT_FILE = 'data.json'

def _convert_to_keycode(key):
    if key.lower() in 'abcdefghijklmnopqrstuvwxyz0123456789':
        return ord(key)
    else:
        return pyHook.HookConstants.VKeyToID('VK_' + key.upper())

def get_xy_in_screen(mx, my):
    wx, wy, ww, wh = get_active_window_dimensions()
    return (mx + wx, my + wy)

def process(events, bmp_directory):
    for record in events:
        event = record['event']
    	print event

        if event == 'wait':
            time.sleep(record['seconds'])        
        elif event == 'keypress':
            win32api.keybd_event(_convert_to_keycode(record['character']), 0, 0, 0)
        elif event == 'keyrelease':
            win32api.keybd_event(_convert_to_keycode(record['character']), 0, win32con.KEYEVENTF_KEYUP, 0)    
        elif event == 'screencap':
            capture_screen(bmp_directory, record['file'])
        elif event == 'mousemove':
            x, y = get_xy_in_screen(record['x'], record['y'])
            win32api.SetCursorPos((x, y)) 
        elif event == 'mousepress':
            x, y = get_xy_in_screen(record['x'], record['y'])

            if record['button'] == 'left':
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y)
            elif record['button'] == 'right':
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y)
            else:
                raise Exception('Unknown button: {}'.format(record['button']))
        elif event == 'mouserelease':
            x, y = get_xy_in_screen(record['x'], record['y'])

            if record['button'] == 'left':
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y)
            elif record['button'] == 'right':
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y)
            else:
                raise Exception('Unknown button: {}'.format(record['button']))

if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    directory = arguments['<directory>']

    with open(os.path.join(directory, INPUT_FILE), 'r') as f:
        events = json.load(f)

    # allow some time to switch windows
    countdown()

    process(events, os.path.join(directory, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
    
