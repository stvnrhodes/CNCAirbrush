This program is used to interface with the CNC Airbrush that Group 13 is creating for ME102B at UC Berkeley.  It can be used from any computer to communicate with the device.  This program is written in python using wxPython and should be cross-platform, working on any computer that has wifi (basically all modern laptops).  It is optimized for Windows.

Command list (All variables are long integers except where specified):
g00 x y z = Move relative to current position
g01 x y z pan tilt= Move based on absolute position
g02 x1 y1 z1 x2 y2 z2 = Go through the stepper motions of making an image
g03 x1 y1 z1 x2 y2 z2 imageData = Make image with corners at current position,
                                  (x1,y1,z1), and (x2,y2,z2).  Imagedata is a
                                  B&W image, in BMP format.
g04 pan = Change pan to the given value (Float between 0 and 1)
g05 tilt = Change tilt to the given value (Float between 0 and 1)
g06 dutycycle hertz  = Turn solenoid on for the specified Hz and duty cycle 
                       (duty cycle is float between 0 and 1, hertz is float)
g07 time = Turn solenoid on for the specified time in ms
g0a = Make everything stop

All commands get a response of the x, y, z, pan, tilt positions

TODO(4/11/2012):
Add option to change tilt to image size
Add option to trigger solenoid (hertz, duty cycle)
Use kinematics to change xyz on tilt
Add options  menu with feedrate, reversing motors
error if transmit byte count is off

Auto update position via events - DONE
Make Run change to Stop when in motion - low priority
Add color changing for altered image - low priority
Allow holding down buttons - low priority
Remove Final Image option - low priority
Add keyboard shortcuts for changing position - low priority
Add double clicking to close preview - low priority

No run if points not selected - DONE
Prevent drawing in upper hemisphere - DONE
Alert for errors - DONE
Only allow running if not editing image size - DONE
Change commands to threads - DONE
Get Sockets working - DONE
Add option to disable solenoid for a run - DONE
Add text saying image size - DONE
Resize preview image based on image size - DONE
No preview if points not selected - DONE
Update status text - DONE


Program that lets you send orders over command line - DONE
Program that sends an image over serial
Parse BMP - DONE
Parse Integer - DONE