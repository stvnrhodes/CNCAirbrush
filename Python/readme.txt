This program is used to interface with the CNC Airbrush that Group 13 is creating for ME102B at UC Berkeley.  It can be used from any computer to communicate with the device.  This program is written in python using wxPython and should be cross-platform, working on any computer that has wifi (basically all modern laptops).  It is optimized for Windows.

Command list (All variables are integers except where specified):
g00 x y z = Move relative to current position
g01 x y z feedrate = Move relative to current position at feedrate steps/s
g02 x1 y1 z1 x2 y2 z2 imageData = Make image with corners at current position,
                                  (x1,y1,z1), and (x2,y2,z2).  Imagedata is a
                                  B&W image, in BMP format.
g03 pan tilt = Change pan and tilt to the given values
g04 solenoid_on = Turn solenoid on or off
g05 x1 y1 z1 x2 y2 z2 = Go through the stepper motions of making an image
g06 = Query for current x, y, z
g07 = Query for current pan and tilt
g28 = Move to home position (minimum x, y, z)
s stepsPerPixel defaultFeedrate = Set various parameters

TODO(4/11/2012):
Get Sockets working - DONE
Make Run change to Stop when in motion
Add option to disable solenoid for a run
Add option to trigger solenoid
Add text saying image size
Add option to change tilt to image size
Resize preview image based on image size
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
Update status text
Check viability of sending floats - Not relecant
Alert for errors
Only allow running if not editing image size
Add options  menu with feedrate, reversing motors, wifly ip address, port