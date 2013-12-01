/* mbed Stepper Library
 * Copyright (c) 2012 Steven Rhodes
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
 
#ifndef LINEARMOTION_H
#define LINEARMOTION_H

#include "mbed.h"
#include "Stepper.h"
#include "Bitmap.h"

typedef struct {
    long x;
    long y;
    long z;
} Vector;

typedef struct {
    Vector one;
    Vector two;
} TwoVectors;

class LinearMotion {

public:

    /** Interpolate to point specified by the vector (relative to current position)
     * 
     * @param Stepper * s1 The x stepper motor
     * @param Stepper * s2 The y stepper motor
     * @param Stepper * s3 The z stepper motor
     * @param DigitalOut * solenoid The solenoid
     * @param bool * pause The variable for pausing
     * @param bool * stop The variable for stopping
     */
    void setStepMotors(Stepper * s1, Stepper * s2, Stepper * s3, DigitalOut * solenoid, bool * pause, bool * stop);

    /** Interpolate to point specified by the vector (relative to current position)
     * 
     * @param Vector length The vector specifying where to go
     * @param int maxSpeed Max speed used to get to position
     * @param bool solenoidOn Whether to have the solenoid on
     */
    void interpolate(Vector length, int maxSpeed, bool solenoidOn);
    void interpolate(Vector length, int maxSpeed);
    
    /** Interpolate to square specified by the vector (relative to current position)
     * 
     * @param Vector basePos Position defining the base of the square
     * @param Vector heightPos Position defining the height of the square
     * @param int maxSpeed Max speed used to get to position
     * @param bool solenoidOn Whether to have the solenoid on
     */
    void interpolateSquare(Vector basePos, Vector heightPos, int maxSpeed, bool solenoidOn);
    
    /** Set various settings for how we do linear motion
     * 
     * @param long steps_per_pixel The number of steps to go per pixel
     * @param long initial_delay The initial speed for linear acceleration
     * @param long step_buffer steps_per_pixel/step_buffer is the size of the gap on either side of a pixel
     */
     void updateSettings(long steps_per_pixel, long initial_delay, long step_buffer);
  
private:
    void doLinearSideways(Vector delta, Vector nextRow, Stepper ** stepMotor, int maxSpeed, bool solenoidOn);
    void doLinear(Vector delta, Stepper** stepMotor, int maxSpeed, bool solenoidOn);
    void enableSteppers(bool en);
    int delayTime (int oldDelay, int stepNumber);
    Stepper * StepMotor[3];
    DigitalOut * _sol;
    Bitmap _bmp;
    bool reversing;
    volatile bool * _paused;
    volatile bool * _stopped;
    bool _z, _z_slantways;
    
    long _steps_per_pixel;
    long _z_steps_per_pixel;
    long _step_buffer; // Make a gap of _steps_per_pixel/_step_buffer  between each pixel
    long _initial_delay; // in us
};
 
 #endif