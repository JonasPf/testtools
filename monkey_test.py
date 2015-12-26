"""Randomly move the mouse and click around to test an application

First write a config file that defines the functions that are run in random order.

Then run monkey_test.py with the desired options. It will first open a window. 
Resize and position the window over the area you want to test. Then click "Start".

If at any time you want to stop the test, press CTRL + F11 (You may need to hold those two keys
for a second).

WARNING: Don't do this on a PC that you can't replace easily. IT does random things on
  your computer. If something is wrong chances are that it deletes all your files or 
  formats your hard disk. I would advise to run this in a virtual machine.

Config Example:
  mouse_random_pos
  mouse_left_up_or_down
  type:'Test'
  key:'enter'
  key:'esc'
  key:'left_arrow'

Usage:
  monkey_test.py --config=<file.csv> [--seed=<number>] ([--actions=<number> | --duration=<minutes>]) [--slow-after=<number>] [(--check-log=<file> <regex>)] [--geometry=<geometry>] [--wait-between=<seconds>]
  monkey_test.py --show-functions [--detail]
  monkey_test.py --show-keys
  monkey_test.py -h | --help

Options:
  --config=<file.csv>        Config file defining the used functions. The format for each line is: function:parameter
  --actions=<number>         How many actions to execute [default: 1000]
  --duration=<minutes>       How many minutes to run. You can use either this or the --actions argument.
  --gemoetry=<geometry>      Size and position of the window. Example: 400x400+100+100
  --check-log=<file> <regex> Check a log file and stop the test if it contains the specified regular expression (E.g. ERROR)
  --slow-after=<number>      Slow down after a certain amount of actions
  --show-keys                Show all available keys (You can also just use an integer for arbitrary keycodes)
  --seed=<number>            Seed to create random numbers. When you want to repeat a series of actions, use the same seed number. [default: 5]
  --wait-between=<seconds>   Wait between actions. Sometimes this is necessary too avoid 'overheating'. Example: 0.01

  --show-functions           Show all available functions
  --detail                   Show all available functions with detail descriptions

  -h --help                  Show this

"""
# TODO: 
#   - Find a way to check if the app crashed and stop the test if thats the case - Implemented but doesn't seem to work
#   - Split into different files

import win32api, win32gui, win32con
import time
import random
import datetime
import docopt 
import sys, inspect, csv, re
import winxpgui
import Tkinter as tk

INDENT = "=> "

# Global variables (yeah, I know they are evil ... but convenient)
destination = None
log_file = None
arguments = None
toplevel_window = None

######################
# basic functionality
######################

VK_CODE = {'backspace':0x08,
    'tab':0x09,
    'clear':0x0C,
    'enter':0x0D,
    'shift':0x10,
    'ctrl':0x11,
    'alt':0x12,
    'pause':0x13,
    'caps_lock':0x14,
    'esc':0x1B,
    'spacebar':0x20,
    'page_up':0x21,
    'page_down':0x22,
    'end':0x23,
    'home':0x24,
    'left_arrow':0x25,
    'up_arrow':0x26,
    'right_arrow':0x27,
    'down_arrow':0x28,
    'select':0x29,
    'print':0x2A,
    'execute':0x2B,
    'print_screen':0x2C,
    'ins':0x2D,
    'del':0x2E,
    'help':0x2F,
    '0':0x30,
    '1':0x31,
    '2':0x32,
    '3':0x33,
    '4':0x34,
    '5':0x35,
    '6':0x36,
    '7':0x37,
    '8':0x38,
    '9':0x39,
    'a':0x41,
    'b':0x42,
    'c':0x43,
    'd':0x44,
    'e':0x45,
    'f':0x46,
    'g':0x47,
    'h':0x48,
    'i':0x49,
    'j':0x4A,
    'k':0x4B,
    'l':0x4C,
    'm':0x4D,
    'n':0x4E,
    'o':0x4F,
    'p':0x50,
    'q':0x51,
    'r':0x52,
    's':0x53,
    't':0x54,
    'u':0x55,
    'v':0x56,
    'w':0x57,
    'x':0x58,
    'y':0x59,
    'z':0x5A,
    'numpad_0':0x60,
    'numpad_1':0x61,
    'numpad_2':0x62,
    'numpad_3':0x63,
    'numpad_4':0x64,
    'numpad_5':0x65,
    'numpad_6':0x66,
    'numpad_7':0x67,
    'numpad_8':0x68,
    'numpad_9':0x69,
    'multiply_key':0x6A,
    'add_key':0x6B,
    'separator_key':0x6C,
    'subtract_key':0x6D,
    'decimal_key':0x6E,
    'divide_key':0x6F,
    'F1':0x70,
    'F2':0x71,
    'F3':0x72,
    'F4':0x73,
    'F5':0x74,
    'F6':0x75,
    'F7':0x76,
    'F8':0x77,
    'F9':0x78,
    'F10':0x79,
    'F11':0x7A,
    'F12':0x7B,
    'F13':0x7C,
    'F14':0x7D,
    'F15':0x7E,
    'F16':0x7F,
    'F17':0x80,
    'F18':0x81,
    'F19':0x82,
    'F20':0x83,
    'F21':0x84,
    'F22':0x85,
    'F23':0x86,
    'F24':0x87,
    'num_lock':0x90,
    'scroll_lock':0x91,
    'left_shift':0xA0,
    'right_shift ':0xA1,
    'left_control':0xA2,
    'right_control':0xA3,
    'left_menu':0xA4,
    'right_menu':0xA5,
    'browser_back':0xA6,
    'browser_forward':0xA7,
    'browser_refresh':0xA8,
    'browser_stop':0xA9,
    'browser_search':0xAA,
    'browser_favorites':0xAB,
    'browser_start_and_home':0xAC,
    'volume_mute':0xAD,
    'volume_Down':0xAE,
    'volume_up':0xAF,
    'next_track':0xB0,
    'previous_track':0xB1,
    'stop_media':0xB2,
    'play/pause_media':0xB3,
    'start_mail':0xB4,
    'select_media':0xB5,
    'start_application_1':0xB6,
    'start_application_2':0xB7,
    'attn_key':0xF6,
    'crsel_key':0xF7,
    'exsel_key':0xF8,
    'play_key':0xFA,
    'zoom_key':0xFB,
    'clear_key':0xFE,
    '+':0xBB,
    ',':0xBC,
    '-':0xBD,
    '.':0xBE,
    '/':0xBF,
    '`':0xC0,
    ';':0xBA,
    '[':0xDB,
    '\\':0xDC,
    ']':0xDD,
    "'":0xDE,
    '`':0xC0} 

def mouse_left_down():
    """
    Press the left mouse button
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)

def mouse_left_up():
    """
    Release the left mouse button. 

    Warning: This usually doesn't happen if there was no mouse_left_down event first. For a more realistic behaviour use mouse_left_up_or_down()
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def mouse_wheel_up(n):
    """
    Roll wheel up
    
    Parameters:
      n - How many 'steps'
    """
    for i in range(0, n):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,120) 
        time.sleep(0.001) # without this delay, windows won't recognise multiple wheel changes

def mouse_wheel_down(n):
    """
    Roll wheel down
    
    Parameters:
      n - How many 'steps'
    """
    for i in range(0, n):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,-120 * n) 
        time.sleep(0.001) # without this delay, windows won't recognise multiple wheel changes
        
def key_down(key):
    """
    Press a key
    
    Parameters:
      key - Key description or code, see http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
    """
    win32api.keybd_event(_convert_to_keycode(key), 0, 0, 0)

def key_up(key):
    """
    Release a key

    Warning: This usually doesn't happen if there was no key_down event first.
    
    Parameters:
      key - Key description or code, see http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
    """
    win32api.keybd_event(_convert_to_keycode(key), 0, win32con.KEYEVENTF_KEYUP, 0)    

def mouse_pos(p):
    """
    Move the mouse
    
    Parameters:
      p - A tuple with x, y
    """
    global destination
    win32api.SetCursorPos((destination[0] + p[0], destination[1] + p[1])) 

def sleep(s):
    """
    Wait x amount of seconds

    Parameters:
      s - seconds (e.g. 1, 0.5)
    """
    time.sleep(s)

#######################################
# Composed of multiple basic functions
#######################################

is_mouse_left_down = False
def mouse_left_up_or_down():
    """
    Press or release left mouse button depending on its current state
    """
    global is_mouse_left_down

    if is_mouse_left_down:
        print INDENT + "up"
        mouse_left_up()
    else:
        print INDENT + "down"
        mouse_left_down()

    is_mouse_left_down = not is_mouse_left_down

def drag(new_pos):
    """
    Drags the mouse
    
    Parameters:
      new_pos - A tuple with x, y
    """
    mouse_left_down()
    time.sleep(0.015) # doesn't work without delay
    mouse_pos(new_pos)
    time.sleep(0.015)
    mouse_left_up()

def drag_random():
    """
    Drags the mouse to a random position    
    """
    global destination
    pos = _random_pos(destination)
    print INDENT + str(pos)
    drag(pos)

def mouse_left_click():
    """
    Quickly click with the left mouse button
    """
    mouse_left_down()
    mouse_left_up()

def key(key):
    """
    Press and release a key
    
    Parameters:
      key - Key description or code, see http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
    """
    key_down(key)
    key_up(key)

def _horizontal_range(rect):
    return (rect[0], rect[0] + rect[2])

def _vertical_range(rect):
    return (rect[1], rect[1] + rect[3])

def _random_pos(destination):
    x = random.randint(*_horizontal_range(destination)) - destination[0]
    y = random.randint(*_vertical_range(destination)) - destination[1]
    return (x, y)

def mouse_random_pos():
    """
    Move the mouse to a random position within the selected window
    """
    global destination
    pos = _random_pos(destination)
    print INDENT + str(pos)
    mouse_pos(pos)

def key_random():
    """
    Press and release a random key
    """
    random_key = random.choice(VK_CODE.keys())
    print INDENT + random_key
    key(VK_CODE[random_key])

def type(str):
    """
    Type in a string.

    Parameters:
      str - String to type
    """
    for c in str:
        key(c)

######################
# Some helper methdds
######################

def _convert_to_keycode(key):
    if isinstance(key, basestring):
        key = VK_CODE[key.lower()]
    return key

def _get_available_functions():
    functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    return {f[0]:f[1] for f in functions if f[0][0] != '_'}

def _show_functions():
    global arguments

    for name, func in sorted(_get_available_functions().items(), key=lambda x: x[0]):
        if arguments['--detail']:
            print "---------------"
            print name
            print "---------------"
            print (func.__doc__ if func.__doc__  else "\n    No documentation!\n")
        else:
            print name

def _exit():
    global log_file
    if log_file:
        log_file.close()

def _exit_if_log_error(arguments):
    global log_file

    if log_file:
        text = log_file.read()

        if re.search(arguments['<regex>'], text):
            print "{} found in {}. Stopping test.".format(arguments['<regex>'], arguments['--check-log'])
            sys.exit(1)

def _exit_if_shortcut():
    if win32api.GetAsyncKeyState(VK_CODE['F11']) != 0 and win32api.GetAsyncKeyState(VK_CODE['ctrl']) != 0:
       print "Exit because CTRL + F11 was pressed"
       sys.exit(0)

started = None
def _check_duration(arguments):
    global started

    if started is None:
        started = datetime.datetime.now()

    diff = datetime.datetime.now() - started
    if (diff.days * 1440) + (diff.seconds / 60) > int(arguments['--duration']):
        print "Exit because over {} minutes".format(arguments['--duration'])
        sys.exit(0)

def _exit_if_necessary(arguments, action):
    if arguments['--duration']:
        _check_duration(arguments)
    elif arguments['--actions']:
        if action > int(arguments['--actions']):
            sys.exit(0)

def _run_functions():
    global arguments

    with open(arguments['--config'], 'r') as myfile:
        lines = myfile.readlines()
        available_functions = _get_available_functions()
        functions = []

        for line in lines:
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                split = line.split(':')
                function = available_functions[split[0]]
                parameter = eval(split[1]) if len(split) > 1 else None
                functions.append((function, parameter))

        action = 0
        while True:
            action += 1
            _exit_if_necessary(arguments, action)
            _exit_if_shortcut()
            _exit_if_log_error(arguments)

            if arguments['--slow-after'] and action > int(arguments['--slow-after']):
                time.sleep(5)

            function, parameter = random.choice(functions)

            print "{}. {}{}".format(action, function.__name__, "" if parameter is None else ":" + repr(parameter))

            if parameter is None:
                function()
            else:
                function(parameter)

            if arguments['--wait-between']:
                time.sleep(float(arguments['--wait-between']))

    exit()

def _get_client_rect(handle):
    rect = win32gui.GetClientRect(handle)
    x, y = win32gui.ClientToScreen(handle, (rect[0], rect[1]))
    destination = (x, y, rect[2], rect[3])
    
    return destination

def _create_window(arguments):
    global toplevel_window

    toplevel_window = tk.Tk(className='Position this window over the test area!')
    toplevel_window.config(height = 300, width = 300)
    toplevel_window.geometry(arguments['--geometry']) 
    toplevel_window.attributes('-alpha', 0.7)
    button = tk.Button(toplevel_window, bg='red', text='Start', command=_start)
    button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    toplevel_window.mainloop()

def _start():
    global destination
    global log_file

    print "Window geometry: {}".format(toplevel_window.geometry())
    destination = _get_client_rect(toplevel_window.winfo_id())
    print "Will perform monkey test in region: {0}".format(destination)
    toplevel_window.destroy()

    random.seed(arguments['--seed'])

    if arguments['--check-log']:
        log_file = open(arguments['--check-log'], 'r')

    print "Click once to focus window"
    mouse_left_click()

    _run_functions()

def _show_keys():
    print '\n'.join(sorted(VK_CODE.keys()))

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)

    if arguments['--show-functions']:
        _show_functions()
    elif arguments['--show-keys']:
        _show_keys()
    else:
        _create_window(arguments)
