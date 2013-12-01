#ifndef IMGBUFFER_H
#define IMGBUFFER_H

#define MAX_IMG_BUF 1024

class ImgBuffer {
public:
    ImgBuffer() {
        write = 0;
        read = 0;
        size = MAX_IMG_BUF + 1;
    };

    bool isFull() {
        return ((write + 1) % size == read);
    };

    bool isEmpty() {
        return (read == write);
    };

    void queue(uint8_t k) {
        if (isFull()) {
            read++;
            read %= size;
        }
        buf[write++] = k;
        write %= size;
    }

    uint16_t available() {
        return (write >= read) ? write - read : size - read + write;
    };

    bool dequeue(uint8_t * c) {
        if (!isEmpty()) {
            *c = buf[read++];
            read %= size;
        }
        return(!isEmpty());
    };

   void clear() {
       read = write;
   };

private:
    volatile uint16_t write;
    volatile uint16_t read;
    uint16_t size;
    uint8_t buf[MAX_IMG_BUF + 1];
};

#endif