/**
* @author Steven Rhodes
*
* @section LICENSE
*
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

#ifndef BITMAP_H
#define BITMAP_H

#include "mbed.h"

class Bitmap {
public:
    /**
    * Constructor to deal with bitmap
    */
    Bitmap ();

    /**
    * Load an image into the bitmap.
    *
    * @return true if the image is successfully loaded
    */
    bool openImg(char* filename);

    /**
    * Change the row we're looking at.
    *
    * @return true if successful.
    */
    bool setRow(int row);

    /**
    * Get whether we should draw a pixel at the given spot
    * 
    * @param pixel The pixel to check
    * @param reversed Whether to reverse the pixel
    * @return true if there's a pixel.
    */
    bool isPixel(int pixel, bool reversed);
    bool isPixel(int pixel);

    /**
    * Get whether it's a blank row
    * 
    * @return true if there are  no pixels in the row
    */
    bool isBlankRow(void);

    /**
    * Return the height of the bitmap
    *
    * @return height
    */
    int getHeight();

    /**
    * Return the width of the bitmap
    *
    * @return width
    */
    int getWidth();
    
    /**
    * Close the image when we're done with it
    *
    * @return true if properly closed
    */
    bool closeImg(void);
    
private:
    FILE * fp;
    bool loaded;
    long offset, width, height, row_size, row_num;
    char * row_data;
    
    /**
    * Get the pixel at a position
    * @param pixel column
    *
    * @return true if the pixel is black
    */
    bool pixel(int column);

};
#endif