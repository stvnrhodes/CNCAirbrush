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
#ifndef STEPPER_H
#define STEPPER_H

#include "mbed.h"

class Stepper {

public:

    /** Create a stepper object connected to the specified clk pin and dir pin
     *
     * @param pin step pin to trigger for steps 
     * @param pin dir pin to choose direction
     * @param pin en pin to enable the motor
     */
    Stepper(PinName step, PinName dir, PinName en);
    
    /** Turn on the stepper motor
     * @param direction 1 for away from motor or 0 for towards motor
     */
    void stepOn(bool direction);  
    
    /** Turn off the stepper motor **/
    void stepOff(void);
    
    /** Enable the motor 
     * @param en Whether to enable the motor
     */
    void enable(bool en);
 
    /** Set the position of the motor to a new offset
     * @param long position The position we set it to
     */
    void setPosition(long position);
 
    /** Get the position of the motor
     @return current position of the stepper motor
     */   
    long getPosition(void);
  
private:  
    DigitalOut _step;
    DigitalOut _dir;
    DigitalOut _en;
    long _position;
     
};

#endif