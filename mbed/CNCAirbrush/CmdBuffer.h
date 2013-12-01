#ifndef CMDBUFFER_H
#define CMDBUFFER_H

#define MAX_CMD_BUF 16
#define MAX_CMD_NUM 0xb
#define MAX_INTERRUPTS 3

// Command Struct
typedef struct {
    char cmd;
    union {
        float f[6];
        long l[6];
    };       
} Command;

class CmdBuffer {
public:
    CmdBuffer() {
        write = 0;
        read = 0;
        size = MAX_CMD_BUF + 1;
        temp_ptr = 0;
        temp_size = 2 + 6*9;
        cmd_sizes[0x0] = 3;
        cmd_sizes[0x1] = 5;
        cmd_sizes[0x2] = 6;
        cmd_sizes[0x3] = 6;
        cmd_sizes[0x4] = 1;
        cmd_sizes[0x5] = 1;
        cmd_sizes[0x6] = 4;
        cmd_sizes[0x7] = 1;
        cmd_sizes[0x8] = 0;
        cmd_sizes[0x9] = 0;
        cmd_sizes[0xa] = 0;
        interrupt_cmds[0] = 0xff;
        interrupt_cmds[1] = 0xff;
        interrupt_cmds[2] = 0xff;
    };

    bool isFull() {
        return ((write + 1) % size == read);
    };

    bool isEmpty() {
        return (read == write);
    };

    // Return true if we've queued a command
    bool queue(char k) {
        tempbuf[temp_ptr++] = k;
        if (temp_ptr == 2) {
            int cmd_num = (0x0f&char_to_num(tempbuf[1]))|(0xf0&char_to_num(tempbuf[0])<<4);
            if (cmd_num > MAX_CMD_NUM) { //Invalid
                temp_ptr = 0;
                temp_size = 4 + 6*9;
                return true;
            } else {
                temp_size = 2 + 9 * cmd_sizes[cmd_num];
            }
        }
        if (temp_ptr >= temp_size) {
            Command c;
            c.cmd = (0x0f&char_to_num(tempbuf[1]))|(0xf0&char_to_num(tempbuf[0])<<4);
            for (int i = 0; i < cmd_sizes[c.cmd]; i++) {
                c.l[i] = str_to_long(tempbuf + 3 + i*9);
#ifdef DEBUG
                printf("arg%d: %x\n\r",i,c.l[i]);
#endif
            }
            for (int i = 0; i < MAX_INTERRUPTS; i++) {
                if (c.cmd == interrupt_cmds[i]){
                    interrupt_funcs[i](&c);
                }
            }
            queue_cmd(c);
            temp_ptr = 0;
            temp_size = 4 + 6*9;
            return true;
        }
        return false;
    }

    uint16_t available() {
        return (write >= read) ? write - read : size - read + write;
    };

    Command * dequeue() {
        Command * c = NULL;
        if (!isEmpty()) {
            c = &buf[read++];
            read %= size;
        }
        return c;
    };
    
    bool attach_interrupt(char cmd, void (*func)(Command *), int num) {
        if (num < MAX_INTERRUPTS) {
            interrupt_funcs[num] = func;
            interrupt_cmds[num] = cmd;
            return true;
        }
        return false;
    }

private:
    void queue_cmd(Command k) {
        if (isFull()) {
            read++;
            read %= size;
        }
        buf[write++] = k;
        write %= size;
    }
    
    // Return 0xf if char is invalid
    char char_to_num(char c) {
        if(c >= '0' && c <= '9') {
            return c - '0';
        } else if(c >= 'a' && c <= 'f') {
            return c - 'a' + 0xa;
        } else if(c >= 'A' && c <= 'F') {
            return c - 'A' + 0xa;
        } else {
#ifdef DEBUG
            printf("CmdBuffer::char_to_num: invalid number\r\n");
#endif
           return 0xf;
        }      
    }

    long str_to_long(char * str) {
        long ans = 0;
        for (int i = 7; (i > 0 && i < 8); i -= 2) {
            ans = ans << 8;
            ans |= (0xf0 & char_to_num(str[i - 1])<<4);
            ans |= (0x0f & char_to_num(str[i]));
        }
        return ans;
    }

    volatile uint16_t write;
    volatile uint16_t read;
    uint16_t size;
    void (*interrupt_funcs[MAX_INTERRUPTS])(Command *);
    char interrupt_cmds[MAX_INTERRUPTS];
    Command buf[MAX_CMD_BUF + 1];
    volatile uint16_t temp_ptr;
    volatile uint16_t temp_size;
    char tempbuf[2 + 6*9 + 1];
    uint16_t cmd_sizes[MAX_CMD_NUM];
};

#endif