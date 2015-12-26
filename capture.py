"""Capture mouse and keyboard events

Usage:
  capture.py <directory>

Options:
  -h --help    show this
"""

import pythoncom, pyHook, sys, json, os, shutil, sys

from common import *

import threading
import datetime
import docopt

OUTPUT_FILE = 'data.json'
BMP_DIRECTORY = 'expected'
last_event = None
directory = None

last_event = None
running = True
events = []

screenshot_count = 0
screenshot_directory = None


def calc_time_diff():
    global last_event

    new_event = datetime.datetime.now()
    diff = new_event - last_event
    last_event = new_event

    return diff.total_seconds()

def get_xy_in_window(mx, my):
    wx, wy, ww, wh = get_active_window_dimensions()
    return (mx - wx, my - wy)

def mouse_event(event):
    mx, my = event.Position
    x, y = get_xy_in_window(mx, my)

    append_wait_event()

    if event.MessageName == 'mouse move':
        events.append({'event' : 'mousemove', 'x' : x, 'y' : y})
    elif event.MessageName == 'mouse left up':
        events.append({'event' : 'mouserelease', 'button' : 'left', 'x' : x, 'y' : y})
    elif event.MessageName == 'mouse left down':
        events.append({'event' : 'mousepress', 'button' : 'left', 'x' : x, 'y' : y})
    elif event.MessageName == 'mouse right up':
        events.append({'event' : 'mouserelease', 'button' : 'right', 'x' : x, 'y' : y})
    elif event.MessageName == 'mouse right down':
        events.append({'event' : 'mousepress', 'button' : 'right', 'x' : x, 'y' : y})
    else:
        raise Exception('Unknown event: {}'.format(event.MessageName))

    return True


def screenshot():
    global screenshot_count, screenshot_directory

    print 'Save screen capture'
    screenshot_count += 1;
    filename = '{}.bmp'.format(screenshot_count)
    capture_screen(screenshot_directory, filename)
    return filename


def append_wait_event():
    diff = calc_time_diff()
    events.append({'event' : 'wait', 'seconds' : diff})

def keyboard_event(event):
    global running

    print event.GetKey()

    if event.MessageName in ('key down', 'key sys down'):
        if event.Key == 'F11':
            running = False
        elif event.Key == 'F12':
            filename = screenshot()
            append_wait_event()
            events.append({'event' : 'screencap', 'file' : filename})
        else:
            append_wait_event()
            events.append({'event' : 'keypress', 'character' : event.Key})
    elif event.MessageName in ('key up', 'key sys up'):
        if event.Key == 'F12':
            pass # ignore F12 key up events
        else:
            append_wait_event()
            events.append({'event' : 'keyrelease', 'character' : event.Key})
    else:
        raise Exception('Unknown event: {}'.format(event.MessageName))

    return True

def write_events(events, directory):
    filename = os.path.join(directory, OUTPUT_FILE)

    print 'Write to {}'.format(filename)

    with open(filename, 'w') as f:
        json.dump(events, f, indent=4)

    sys.exit(0)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print 'Error: {} already exists'.format(directory)
        sys.exit(1)

if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    create_directory(arguments['<directory>'])
    screenshot_directory = os.path.join(arguments['<directory>'], BMP_DIRECTORY)
    countdown()

    last_event = datetime.datetime.now()

    hm = pyHook.HookManager()
    hm.MouseAll = mouse_event
    hm.KeyAll = keyboard_event
    hm.HookMouse()
    hm.HookKeyboard()

    print 'Start capturing (Exit with F11, Screenshot with F12)'

    while running:
        pythoncom.PumpWaitingMessages()

    print 'End capturing'

    write_events(events, arguments['<directory>'])
