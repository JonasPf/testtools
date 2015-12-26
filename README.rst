These are a couple of testing tools I'm working on at the moment. At the
moment there are just a bunch of scripts to try out various ideas I'm having.
Don't expect fancy install scripts or even a python egg.

Requirements:
  - Windows (Sorry!)
  - pyHook: http://sourceforge.net/projects/pyhook/postdownload?source=dlp
  - docopt: pip install docopt
  - pywin32: http://sourceforge.net/projects/pywin32/files/

monkey_test.py
==============

Description
-----------

Similar to http://developer.android.com/tools/help/monkey.html for Android,
this script simulates pseudo-random user input on a Windows Application. For example mouse movement, clicks, keyboard input, ...

Use case
--------

Test software by sending a huge amount of user input to it. This is a very
low-cost test. A configuration can be set up in a couple of minutes. If run
long enough eventually it will execute a combination of user inputs that will
cause a bug in the program under test (That's the theory anyway).

Usage
-----

The kind of user inputs performed can be configured in a configuration file.
Each line contains a user input. During runtime the program rnadomly chooses
from those lines and performs the corresponding user input.

The basic format of a line is: action:parameter

Example:

  mouse_left_up_or_down
  type:'Test'
  key:'enter'


The following command shows all possible user inputs with their parameters:

  python monkey_test.py --show-functions --detail


Some user inputs aks for keys as parameters. A list of all valid keys can be
shown with:

  python monkey_test.py --show-keys


To start the test, run:

  python monkey_test.py --config FILE

A semi-transparent window will appear. Drag and resize the window so that it
covers the area to test (user inputs will only be executed within this window)
and hit the red start button. By default 1000 user inputs will be simulated.

To increase that value use:

  python monkey_test.py --config FILE --actions=2000

Alternatively it is possible to specify how long (in minutes) the test should
run:

  python monkey_test.py --config FILE --duration=5

The test will usually run until the end. This poses a problem if, for example,
the program under test crashes during the test, it will continue simulating
user inputs. Whatever was under underneath the program under test will receive
those user inputs (possibly the windows desktop). To avoid this problem it is
possible to monitor a log file and stop the user inputs if certain strings
appear in the log file:

  python monkey_test.py --config FILE --check-log C:\test.log ERROR

Regardless, I always recommend to run monke_test.py in a disposable VM. There
is just too much that can go wrong if random inputs are send to a PC. Don't
blame me if you accidentally format your disk!

Running monkey test again will result in exactly the same user inputs so you
can run it again to reproduce issues. the only problem is that it often runs
to fast to be able to observe anything. It is possible to slow it down after a
certain amount of user inputs. If you simulate 1000 user inputs and you notice a problem after about half of it, it makes sense to slow down after 450 user inputs to be able to see what is happening:

  python monkey_test.py --config FILE --slow-after 450

More options are described in the help:

  python monkey_test.py --help


capture.py / replay.py
======================

Description
-----------

capture.py: Captures user input like mouse movement and keys. When pressing a special key (F12) it takes a screenshot.

replay.py: Replays previously captured user input. It also takes screenshots
at the same stages as during the capture.


Use case
--------

There are two use cases:

1. A tester can run this tool in the background while testing a software. When
a bug is found it can easily be easily reproduced.

2. It can act as a quick & dirty regression test for developers. Before making
any changes to the code, the developer can click through all functionality in
the software and take screenshots regularly. After modifying the code, the
developer can replay the previously recorded actions. This will result in two
sets of screenshots. One from before the modification and one after. These
screenshots can then be compared and checked for (unwanted) differences. A
tool like http://www.imagemagick.org/script/compare.php can help with this.

Usage
-----

To capture inputs:

  python capture.py TEST_FOLDER

While capturing there are two special keys:

  F12: Takes a screenshot and saves it into a folder 'expected' under the
specified test folder
  F11: Stops the recording

To replay inputs:

  python replay.py TEST_FOLDER

Screenshots will be taken and put in a folder with the current date/time as
its name.

The input will always be recorded relative to the current active window. This
ensures that the replay will still work even if the window has been moved in
the meantime.

