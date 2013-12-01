#include "Stepper.h"

Stepper::Stepper(PinName step, PinName dir, PinName en) : _step(step), _dir(dir), _en(en) {
    _step = 0, _dir = 0, _en = 1;
    _position = 0;
}

void Stepper::stepOn(bool direction) {
    _dir = direction;
    if (direction) {
        _position++;
    } else {
        _position--;
    }
    _step = 1;
}

void Stepper::stepOff(void) {
    _step = 0;
}

void Stepper::enable(bool en) {
    _en = !en;
}

void Stepper::setPosition(long position) {
    _position = position;
}

long Stepper::getPosition(void) {
    return _position;
}