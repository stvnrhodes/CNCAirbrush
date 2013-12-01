#include "mbed.h"
#include "Wifly.h"
#include <string>

// #define DEBUG


Wifly::Wifly(   PinName tx, PinName rx, PinName _reset, char * ssid, char * ip, char * netmask, int channel, int baudrate):
        wifi(tx, rx), reset_pin(_reset) {
    wifi.baud(baudrate);
    wifi.format(8, Serial::None, 1);
    adhoc = true;
    strcpy(this->ssid, ssid);
    strcpy(this->ip, ip);
    strcpy(this->netmask, netmask);
    this->channel = channel;
    last_char = '\0';
    reset();
}


void Wifly::handler_rx(void) {
    char read = wifi.getc();
    if(read == 'q') {
        attach_img(true);
        gettingImg = true;
        last_char = read;
    } else if(read == 'g'){
        attach_cmd(true);
    } else {
        buf_wifly.queue(read);
    }
    //call user callback
    rx.call();
}

void Wifly::handler_img(void) {
    char read = wifi.getc();
   // printf("%c", read);
    if (read == '*') {
      gettingImg = false;
      gotImg = true;
      attach_img(false);
      attach_rx(true);
    }
    img_buffer.queue(read);
 //   printf("%d",img_buffer.available());
    if (img_buffer.isFull()) {
        write_img();
    }
}

void Wifly::handler_cmd(void) {
    char read = wifi.getc();
    if (cmd_buffer.queue(read)) {
        attach_rx(true);
    }
}

void Wifly::attach_rx(bool null) {
    if (!null) {
        wifi.attach(NULL);
    } else {
        wifi.attach(this, &Wifly::handler_rx);
    }
}

void Wifly::write_img(void) {
    printf("\n\rWriting Image\n\r");
    fp = fopen("/local/pic.bmp", "a");
    char a, c;
    while (!img_buffer.isEmpty()) {
        img_buffer.dequeue((uint8_t *) &c);
        a = (char_to_num(c)<<4) & 0xf0;
        img_buffer.dequeue((uint8_t *) &c);
        a |= char_to_num(c) & 0x0f;
        printf("%x",a);
        fwrite(&a, 1, sizeof(char), fp);
    }
    fpos_t pos;
    fgetpos(fp,&pos);
    fclose(fp);
    wifi.printf("Did it!");
}        

void Wifly::attach_img(bool null) {
    printf("img ");
    if (!null) {
        wifi.attach(NULL);
        if (!img_buffer.isEmpty()) {
            write_img();
        }
        printf("end\n\r");
    } else {
        printf("start\n\r");
        remove("/local/pic.bmp");
        img_buffer.clear();
        wifi.attach(this, &Wifly::handler_img);
    }
}

void Wifly::attach_cmd(bool null) {
    if (!null)
        wifi.attach(NULL);
    else
        wifi.attach(this, &Wifly::handler_cmd);
}

bool Wifly::send(char * str, char * ACK, char * res) {
    char read;
    size_t found = string::npos;
    string checking;
    Timer tmr;

#ifdef DEBUG
    printf("will send: %s\r\n",str);
#endif


    attach_rx(false);
    if (!strcmp(ACK, "NO")) {
        wifi.printf("%s", str);
    } else {
        //We flush the buffer
        while (wifi.readable()){
           wifi.getc();
        }

        tmr.start();
        wifi.printf("%s", str);

        while (1) {
            if (tmr.read() > 3) {
                //We flush the buffer
                while (wifi.readable())
                    wifi.getc();
#ifdef DEBUG
                printf("check: %s\r\n", checking.c_str());
#endif
                attach_rx(true);
                return false;
            } else if (wifi.readable()) {
                read = wifi.getc();
                if ( read != '\r' && read != '\n') {
                    checking += read;
                    found = checking.find(ACK);
                    if (found != string::npos) {
                        wait(0.01);

                        //We flush the buffer
                        while (wifi.readable())
                            wifi.getc();

                        break;
                    }
                }
            }
        }
#ifdef DEBUG
        printf("check: %s\r\n", checking.c_str());
#endif
        attach_rx(true);
        return true;
    }

    //the user wants the result from the command (ACK == "NO", res != NULL)
    if ( res != NULL) {
        int i = 0;
        Timer timeout;
        timeout.start();
        while (1) {
            if (timeout.read() > 3) {
                read = NULL;
                return false;
            } else {
                if (tmr.read_ms() > 500) {
                    res[i] = 0;
#ifdef DEBUG
                    printf("user str: %s\r\n", res);
#endif
                    attach_rx(true);
                    return true;
                }
                if (wifi.readable()) {
                    tmr.start();
                    read = wifi.getc();
                    if ( read != '\r' && read != '\n') {
                        res[i++] = read;
                    }
                }
            }
        }
    }
    attach_rx(true);
    return true;
}

bool Wifly::attach_interrupt(char cmd, void (*func)(Command *), int num) {
    return cmd_buffer.attach_interrupt(cmd, func, num);
}

bool Wifly::hasCmd() {
    return cmd_buffer.available();
}

Command * Wifly::getCmd() {
    Command * c = NULL;
    if (cmd_buffer.available()){
        c = cmd_buffer.dequeue();
    }
    return c;
}

bool Wifly::sendCmd(Command * c){
    char str[4 + 5*9];
    str[0] = 'g';
    str[1] = '0';
    str[2] = num_to_char(c->cmd);
    str[3] = ' ';
    switch(c->cmd){
    case 7:
        for (int i=0; i < 5; i++) {
            long_to_str(str + 4 + 9*i, c->l[i]);
        }
        str[4 + 5*9 - 1] = '\0';
        return send(str);
    case 9:
        for (int i=0; i < 2; i++) {
            long_to_str(str + 4 + 9*i, c->l[i]);
        }
        str[4 + 2*9 - 1] = '\0';
        return send(str);
    case 8:
    default:
        for (int i=0; i < 5; i++) {
            long_to_str(str + 4 + 9*i, c->l[i]);
            str[12 + 9 * i] = ' ';
        }
        str[4 + 5*9 - 1] = '\0';
        return send(str);
    }
}    

bool Wifly::createAdhocNetwork() {
    if (adhoc) {
        char cmd[50];

        if (!cmdMode()) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: Failed to enter cmd mode.  Retrying...\r\n");
#endif
            if (!cmdMode()) {
 #ifdef DEBUG
                printf("Wifly::CreateAdhocNetwork: Cannot enter cmd mode.\r\n");
#endif
               exit();
                return false;
            }
        }

        if (!send("set w j 4\r", "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set join 4\r\n");
#endif
            exit();
            return false;
        }

        //no echo
        if (!send("set u m 1\r", "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set no echo\r\n");
#endif
            exit();
            return false;
        }

        //ssid
        sprintf(cmd, "set w s %s\r", ssid);
        if (!send(cmd, "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set ssid\r\n");
#endif
            exit();
            return false;
        }

        sprintf(cmd, "set w c %d\r", channel);
        if (!send(cmd, "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set channel\r\n");
#endif
            exit();
            return false;
        }

        sprintf(cmd, "set i a %s\r", ip);
        if (!send(cmd, "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set ip address\r\n");
#endif
            exit();
            return false;
        }

        sprintf(cmd, "set i n %s\r", netmask);
        if (!send(cmd, "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set netmask\r\n");
#endif
            exit();
            return false;
        }

        if (!send("set i d 0\r", "AOK")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot set dhcp off\r\n");
#endif
            exit();
            return false;
        }

        if (!send("save\r", "Stor")) {
#ifdef DEBUG
            printf("Wifly::CreateAdhocNetwork: cannot save\r\n");
#endif
            exit();
            return false;
        }

        flush();

        send("reboot\r", "NO");
#ifdef DEBUG
        printf("\r\ncreating an adhoc\r\nnetwork: %s\r\nip: %s\r\nnetmask: %s\r\nchannel: %d\r\n\r\n", ssid, ip, netmask, channel);
#endif

        wait(0.1);
        flush();
        return true;
    } else {
#ifdef DEBUG
        printf("Wifly::CreateAdhocNetwork: You didn't choose the right constructor for creating an adhoc mode!\r\n");
#endif
        return false;
    }
}

void Wifly::flush() {
    while (readable())
        getc();
}

bool Wifly::cmdMode() {
    if (!send("$$$", "CMD")) {
#ifdef DEBUG
        printf("Wifly::cmdMode: cannot enter in cmd mode\r\n");
#endif
        return false;
    }
    return true;
}

void Wifly::reset() {
    reset_pin = 0;
    wait(0.2);
    reset_pin = 1;
    wait(0.2);
}

void Wifly::putc(char c) {
    while (!wifi.writeable());
    wifi.putc(c);
}

bool Wifly::read(char * str) {
    int length = buf_wifly.available();
    if (length == 0)
        return false;
    for (int i = 0; i < length; i++)
        buf_wifly.dequeue((uint8_t *)&str[i]);
    str[length] = 0;
    return true;
}

bool Wifly::exit() {
    return send("exit\r", "EXIT");
}


int Wifly::readable() {
    return buf_wifly.available();
}

char Wifly::getc() {
    char c;
    while (!buf_wifly.available());
    buf_wifly.dequeue((uint8_t *)&c);
    return c;
}

char Wifly::num_to_char(char n) {
    if(n <= 9) {
        return n + '0';
    } else if (n >= 0xa && n <= 0xf) {
        return n + 'a' - 0xa;
    } else {
        return 0;
    }
}

void Wifly::long_to_str(char * str, long n) {
    for (int i = 0; i < 8; i += 2) {
        str[i+1] = num_to_char(n & 0x0f);
        n = n >> 4;
        str[i] = num_to_char(n & 0x0f);
        n = n >> 4;
    }
}

void Wifly::float_to_str(char * str, float f) {
    long_to_str(str, (long) f);
}

// Return 0xf if char is invalid
char Wifly::char_to_num(char c) {
    if(c >= '0' && c <= '9') {
        return c - '0';
    } else if(c >= 'a' && c <= 'f') {
        return c - 'a' + 0xa;
    } else if(c >= 'A' && c <= 'F') {
        return c - 'A' + 0xa;
    } else {
        return 0xf;
    }      
}
