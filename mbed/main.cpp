#include "mbed.h"
#include "Wifly.h"
#include "Bitmap.h"
#include "Stepper.h"
#include "LinearMotion.h"
#include "Servo.h"

#define PAN_RANGE 0.0009
#define PAN_DEGREE 90
#define PAN_CENTER 0.0002
#define STEPS_PER_PIXEL_DEFAULT 600
#define INITIAL_DELAY_DEFAULT 1200
#define STEP_BUFFER_DEFAULT 4
#define DEFAULT_FEEDRATE 200

LocalFileSystem local("local");
Serial pc(USBTX, USBRX);
DigitalOut led(LED1);
DigitalOut solenoid(p29);
Wifly wifi(p9, p10, p8);
Command * cmd;
Bitmap bmp;
bool paused = false;
bool stopped = false;

Stepper x(p6,p5,p14);
Stepper y(p24,p27,p28);
Stepper z(p22,p23,p21);
LinearMotion linearMotion;
Servo servoTilt(p25);
Servo servoPan(p26);



/*1B:Blue
1A:Red
2A:Black
2B:Green*/

void savePosition (Vector position, float pan, float tilt) {
    FILE * fp = fopen("/local/hrmm.settings", "w");
    if (fp != NULL) {
        fwrite(&position.x, sizeof(long), 1, fp);
        fwrite(&position.y, sizeof(long), 1, fp);
        fwrite(&position.z, sizeof(long), 1, fp);
        fwrite(&pan, sizeof(float), 1, fp);
        fwrite(&tilt, sizeof(float), 1, fp);
        fclose(fp);
    }
}


void pause(Command * c) {
    paused = !paused;
    printf("paused:%d\n\r", paused);
}

void stop(Command * c) {
    stopped = true;
    paused = false;
}

int main() {
    servoPan.calibrate(PAN_RANGE, PAN_DEGREE, PAN_CENTER);
    float pan = .5;
    float tilt = 0;
    Vector pos = {0, 0, 0};
    FILE * fp = fopen("/local/hrmm.settings", "r");
    if (fp != NULL) {
        fread(&pos.x, sizeof(long), 1, fp);
        fread(&pos.y, sizeof(long), 1, fp);
        fread(&pos.z, sizeof(long), 1, fp);
        fread(&pan, sizeof(float), 1, fp);
        fread(&tilt, sizeof(float), 1, fp);
        fclose(fp);
    }
    x.setPosition(pos.x);
    y.setPosition(pos.y);
    z.setPosition(pos.z);
    servoPan = pan;
    servoTilt = tilt;
    solenoid = 0;
    pc.baud(460800);
    printf("Test Airbrush!\r\n");
    linearMotion.setStepMotors(&x, &y, &z, &solenoid, &paused, &stopped);
    linearMotion.updateSettings(STEPS_PER_PIXEL_DEFAULT, INITIAL_DELAY_DEFAULT, STEP_BUFFER_DEFAULT);
    wifi.createAdhocNetwork();
    wifi.attach_interrupt(0x09, pause, 0);
    wifi.attach_interrupt(0x0a, stop, 1);
    led = 1;
    long paintingFeedrate = DEFAULT_FEEDRATE;
    while (1) {
        while (pc.readable()) {
            wifi.putc(pc.getc());
        }
        while (wifi.readable()) {
            pc.putc(wifi.getc());
        }
        if (wifi.hasCmd()) {
            cmd = wifi.getCmd();
            switch (cmd->cmd) {
                case 0x00: { //relative motion
                    pc.printf("Move to relative coordinates x: %d, y:%d, z:%d\n\r", cmd->l[0], cmd->l[1], cmd->l[2]);
                    Vector finalPos = {cmd->l[0],
                                       cmd->l[1],
                                       cmd->l[2]};
                    linearMotion.interpolate(finalPos,1);
                    break;
                }
                case 0x01: { //move to specified global coordinates
                    Vector relative = {cmd->l[0] - x.getPosition(),
                                       cmd->l[1] - y.getPosition(),
                                       cmd->l[2] - z.getPosition()};
                    pc.printf("Move to global coordinates x:%d, y:%d, z:%d, Tilt:%f, Pan:%f\n\r",cmd->l[0], cmd->l[1], cmd->l[2], z.getPosition(), tilt, pan);
                    linearMotion.interpolate(relative, 10);
                    break;
                }
                case 0x02: { //pretend paint an image
                    Vector baseVector = {cmd->l[0],
                                         cmd->l[1],
                                         cmd->l[2]};

                    Vector heightVector = {cmd->l[3],
                                           cmd->l[4],
                                           cmd->l[5]};
                    pc.printf("Pretend to paint an image with corners at (x:%d, y:%d, z:%d), (x:%d, y:%d, z:%d) and (x:%d, y:%d, z:%d)\n\r", x.getPosition(), y.getPosition(), z.getPosition(), baseVector.x, baseVector.y, baseVector.z, heightVector.x, heightVector.y, heightVector.z);
                    linearMotion.interpolateSquare(baseVector, heightVector, 10, false);
                    break;
                }
                case 0x03: { //paint an image
                    Vector baseVector = {cmd->l[0],
                                      cmd->l[1],
                                      cmd->l[2]};

                    Vector heightVector = {cmd->l[3],
                                        cmd->l[4],
                                        cmd->l[5]};
                    pc.printf("Paint the image with corners at (x:%d, y:%d, z:%d), (x:%d, y:%d, z:%d) and (x:%d, y:%d, z:%d)\n\r", x.getPosition(), y.getPosition(), z.getPosition(),baseVector.x,baseVector.y,baseVector.z,heightVector.x,heightVector.y,heightVector.z);
                    linearMotion.interpolateSquare(baseVector,heightVector,paintingFeedrate,true);
                    break;
                }
                case 0x04: { //change the pan
                    pan = cmd->f[0];
                    servoPan = pan;
                    pc.printf("Change the pan to %f\n\r",pan);
                    break;
                }
                case 0x05: { //change the tilt
                    tilt = cmd->f[0];
                    servoTilt = tilt;
                    pc.printf("Change the tilt to %f\n\r",tilt);
                    break;
                }
                case 0x06: {
                    linearMotion.updateSettings(cmd->l[0], cmd->l[1], cmd->l[2]);
                    paintingFeedrate = cmd->l[3];
                    break;
                    
                }
                case 0x07: { //turn on the solenoid
                    long t = cmd->l[0];
                    if (t)
                      solenoid = 1;
                    else
                      solenoid = 0;
                    break;
                }
                case 0x09: { // We accidentally got to a pause state
                    paused = false;
                    break;
                }
                default: {
                    pc.printf("You should probably do something with case %x\n\r", cmd->cmd);
                    break;
                }
            }
            stopped = false;
            Vector globalPos = {x.getPosition(), y.getPosition(), z.getPosition()};
            savePosition(globalPos, pan, tilt);
            cmd->cmd = 8;
            cmd->l[0] = globalPos.x;
            cmd->l[1] = globalPos.y;
            cmd->l[2] = globalPos.z;
            cmd->f[3] = pan;
            cmd->f[4] = tilt;
            wifi.sendCmd(cmd);
        }
    }
}
