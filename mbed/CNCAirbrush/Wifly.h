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
*
* @section DESCRIPTION
*
* CNCAirbrush Berkeley ME102B Project
*
*/

#ifndef WIFLY_H
#define WIFLY_H

#include "mbed.h"
#include "CBuffer.h"
#include "CmdBuffer.h"
#include "ImgBuffer.h"



/** Wifly Class
 *
 * Example:
 * @code
 * #include "mbed.h"
 * #include "Wifly.h"
 *
 * Wifly wifly(p9, p10, p8);
 * Serial pc(USBTX, USBRX);
 *
 * int main()
 * {
 *   while(1){
 *     if(wifly.hasCmd()){
 *       Command * c;
*        wifly.getCmd(c)
 *       pc.printf("Msg: %d\r\n", c->cmd);
       }
 * }
 * @endcode
 */
class Wifly {

public:
    

    /**
    * Constructor to create an adhoc network
    *
    * @param tx mbed pin to use for tx line of Serial interface
    * @param rx mbed pin to use for rx line of Serial interface
    * @param ssid ssid of the adhoc network which will be created
    * @param ip ip of the wifi module (default: "169.254.1.1")
    * @param netmask netmask (default: "255.255.0.0")
    * @param channel channel (default: "1")
    * @param baudrate speed of the communication (default: 460800)
    */
    Wifly(  PinName tx, PinName rx, PinName reset, char * ssid = "CNCAirbrush", char * ip = "169.254.1.1",
            char * netmask = "255.255.0.0", int channel = 1, int baudrate = 115200);

    /**
    * Send a string to the wifi module by serial port. This function desactivates the user interrupt handler when a character is received to analyze the response from the wifi module.
    * Useful to send a command to the module and wait a response.
    *
    *
    * @param str string to be sent
    * @param ACK string which must be acknowledge by the wifi module. If "ACK" == "NO", no string has to be acknoledged. (default: "NO")
    * @param res this field will contain the response from the wifi module, result of a command sent. This field is available only if ACK = "NO" AND res != NULL (default: NULL)
    *
    * @return true if ACK has been found in the response from the wifi module. False otherwise or if there is no response in 5s.
    */
    bool send(char * str, char * ACK = "NO", char * res = NULL);

    /**
    * Attach an interrupt for the given command
    * 
    * @param cmd command number to trigger the interrupt for
    * @param func function to run on interrupt (must return void)
    * @param num interrupt number (I currently allow up to 3)
    *
    * @return true if interrupt has been attached
    */
    bool attach_interrupt(char cmd, void (*func)(Command *), int num);

    /**
    * Report that there's a command waiting to be read.
    *
    * @return true if there's a command waiting to be read.
    */
    bool hasCmd();

    /**
    * Fetch the most recent command
    *
    * @return the command on top of the stack
    */
    Command * getCmd();

    /**
    * Connect the wifi module to the ssid contained in the constructor.
    *
    * @return true if successfully sent
    */
    bool sendCmd(Command * c);
    

    /**
    * Create an adhoc network with the ssid contained in the constructor
    *
    * @return true if the network is well created, false otherwise
    */
    bool createAdhocNetwork();

    /**
    * Read a string if available
    *
    *@param str pointer where will be stored the string read
    */
    bool read(char * str);


    /**
    * Reset the wifi module
    */
    void reset();

    /**
    * Check if characters are available
    *
    * @return number of available characters
    */
    int readable();

    /**
    * Read a character
    *
    * @return the character read
    */
    char getc();

    /**
    * Flush the buffer
    */
    void flush();

    /**
    * Write a character
    *
    * @param the character which will be written
    */
    void putc(char c);


    /**
    * To enter in command mode (we can configure the module)
    *
    * @return true if successful, false otherwise
    */
    bool cmdMode();


    /**
    * To exit the command mode
    *
    * @return true if successful, false otherwise
    */
    bool exit();


     /**
     *  Attach a member function to call when a character is received.
     *
     *  @param tptr pointer to the object to call the member function on
     *  @param mptr pointer to the member function to be called
     */
    template<typename T>
    void attach(T* tptr, void (T::*mptr)(void)) {
        if ((mptr != NULL) && (tptr != NULL)) {
            rx.attach(tptr, mptr);
        }
    }


    /**
     * Attach a callback for when a character is received
     *
     * @param fptr function pointer
     */
    void attach(void (*fn)(void)) {
        if (fn != NULL) {
            rx.attach(fn);
        }
    }

private:
    Serial wifi;
    DigitalOut reset_pin;
    bool wpa;
    bool adhoc;
    bool dhcp;
    char phrase[30];
    char ssid[30];
    char ip[20];
    char netmask[20];
    char imgpos;
    char last_char;
    int channel;
    FILE *fp;
    CBuffer buf_wifly;
    CmdBuffer cmd_buffer;
    ImgBuffer img_buffer;

    char char_to_num(char c);
    char num_to_char(char n);
    long str_to_long(char * str);
    float str_to_float(char * str);
    void long_to_str(char * str, long n);
    void float_to_str(char * str, float f);
    void attach_rx(bool null);
    void attach_img(bool null);
    void attach_cmd(bool null);
    void handler_rx(void);
    void handler_img(void);
    void handler_cmd(void);
    void write_img(void);

    FunctionPointer rx;
    bool gettingImg;
    bool gotImg;


};

#endif