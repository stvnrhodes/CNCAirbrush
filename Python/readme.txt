This program is used to interface with the CNC Airbrush that Group 13 is creating for ME102B at UC Berkeley.  It can be used from any computer to communicate with the device.  This program is written in python using wxPython and should be cross-platform, working on any computer that has wifi (basically all modern laptops).

Command list (All variables are integers except where specified):
g00 x y z = Move relative to current position
g01 x y z feedrate = Move relative to current position at feedrate steps/s
g02 x1 y1 z1 x2 y2 z2 imageData = Make image with corners at current position, 
                                  (x1,y1,z1), and (x2,y2,z2).  Imagedata is a 
                                  B&W image, in BMP format.
g03 pan tilt = Change pan and tilt to the given values
g28 = Move to home position (minimum x, y, z)
s stepsPerPixel defaultFeedrate = Set various parameters