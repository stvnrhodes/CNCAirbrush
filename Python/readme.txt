This program is used to interface with the CNC Airbrush that Group 13 is creating for ME102B at UC Berkeley.  It can be used from any computer to communicate with the device.  This program is written in python using wxPython and should be cross-platform, working on any computer that has wifi (basically all modern laptops).  It is optimized for Windows.

Command list (All variables are long integers except where specified):
g00 x y z = Move relative to current position
g01 x1 y1 z1 x2 y2 z2 = Go through the stepper motions of making an image
g02 x1 y1 z1 x2 y2 z2 imageData = Make image with corners at current position,
                                  (x1,y1,z1), and (x2,y2,z2).  Imagedata is a
                                  B&W image, in BMP format.
g03 pan = Change pan to the given value (Float between 0 and 1)
g04 tilt = Change tilt to the given value (Float between 0 and 1)
g05 dutycycle hertz  = Turn solenoid on for the specified Hz and duty cycle 
                       (duty cycle is float between 0 and 1, hertz is float)
g06 time = Turn solenoid on for the specified time in ms
g07 = Query for x, y, z, pan, tilt
g08 = Query for current x, y, z
g09 = Query for current pan and tilt
g10 = Make everything stop

g28 = Move to home position (minimum x, y, z)
s stepsPerPixel defaultFeedrate = Set various parameters

TODO(4/11/2012):
Get Sockets working - DONE
Make Run change to Stop when in motion
Add option to disable solenoid for a run - DONE
Add option to trigger solenoid (hertz, duty cycle)
Add text saying image size - DONE
Add option to change tilt to image size
Resize preview image based on image size - Done
No preview if points not selected - DONE
No run if points not selected
Add color changing for altered image
Use kinematics to change image size on image tilt
Autochange image size when zeroing position
Auto update position
Allow holding down buttons
Remove Final Image option
Add keyboard shortcuts for changing position
Add double clicking to close preview
Update status text - DONE
Prevent drawing in upper hemisphere
Alert for errors
Only allow running if not editing image size
Add options  menu with feedrate, reversing motors, wifly ip address, port

Program that lets you send orders over command line
Program that sends an image over serial
Parse BMP
Parse Integer