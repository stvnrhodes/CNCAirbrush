---
layout: post
title: Project Update
author: Robin Young
---

With the project expo in just a week and a half, our group is busy working hard to perfect our CNC Airbrush Painter.

A few updates:

When all of our mechanical parts arrived from [Rockford Ball Screw](//rockfordballscrew.com/), Misumi, TCI Aluminum, Pololu, [Servocity](//www.servocity.com/), and ASCO, we began to build! The first step was to machine our [Rockford ball screws and acme screws](//rockfordballscrew.com/) to size and create threads and tapers on the ends of the screws. Adam had help on the lathe from the student machine shop staff, and our screws ended up fitting nicely into our end mounts.

The next step was to machine mouting holes into our aluminum. The aluminum was specifically picked out with a flatness spec, so that the alignment of our CNC would not be compromised. For this reason, Marc, Adam, and I were very careful when milling out the holes that we needed. After machining all holes, we were ready to begin assembly.

We then built up the ball screw and acme screw assemblies, and constructed the frame from our extruded aluminum we got from Misumi. While the mechanical team was busy with assembly, Steven was busy working on designing and programming our custom PCB.

The stepper motors were coupled to the ball screw and acme screw assemblies, and testing could begin! Adam stayed up late working on stepper motor control of the z-stage, and we determined the optimal driving speed of the motor. After proving our design was successful with the vertical z-stage, we continued on to assemble the x and y stages. For our status update in class on Monday, we demonstrated successful control of the x, y, and z stages.

On the programming side, Steven has been busy programming the GUI and electrical components, including our Wifly connection to enable wireless control, and the mBed microcontroller that serves as the brain of our system. The GUI allows the user to input any image file they would like to draw onto the object, and the image can be filtered to grayscale, red, blue, or green. The system defines a drawing plane using 3 points, and this enables us to paint on 3D objects.

Please check the Gallery for photos of the project!

-Robin