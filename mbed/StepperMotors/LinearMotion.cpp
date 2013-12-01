#include  "LinearMotion.h"


void LinearMotion::setStepMotors(Stepper * s1, Stepper * s2, Stepper * s3, DigitalOut * solenoid, bool * pause, bool * stop) {
    _sol = solenoid;
    StepMotor[0] = s1;
    StepMotor[1] = s2;
    StepMotor[2] = s3;
    reversing = false;
    _paused = pause;
    _stopped = stop;
    
}

void LinearMotion::interpolate(Vector length, int maxSpeed) {
    interpolate(length, maxSpeed, false);
}

void LinearMotion::interpolate(Vector length, int maxSpeed, bool solenoidOn) {
    long tempLength;
    Stepper * tempStep;
    Stepper * reorderedStepMotor[3] = {StepMotor[0], StepMotor[1], StepMotor[2]};

    _z = false;
    if (abs(length.y) > abs(length.x)) {
        tempLength = length.y;
        length.y = length.x;
        length.x = tempLength;
        tempStep = reorderedStepMotor[1];
        reorderedStepMotor[1] = reorderedStepMotor[0];
        reorderedStepMotor[0] = tempStep;
    }
    if (abs(length.z) > abs(length.x)) {
        tempLength = length.z;
        length.z = length.x;
        length.x = tempLength;
        tempStep = reorderedStepMotor[2];
        reorderedStepMotor[2] = reorderedStepMotor[0];
        reorderedStepMotor[0] = tempStep;
        _z = true;
    }    
    
    enableSteppers(true);
    doLinear(length, reorderedStepMotor, maxSpeed, solenoidOn);
    enableSteppers(false);
}

void LinearMotion::interpolateSquare(Vector basePos, Vector heightPos, int maxSpeed, bool solenoidOn) {
    long tempLength;
    Stepper * tempStep;
    
    Stepper * reorderedStepMotor[3] = {StepMotor[0], StepMotor[1], StepMotor[2]};
    Vector homePosition = {-heightPos.x, -heightPos.y, -heightPos.z};
    _z_slantways = false;
    
    if (abs(heightPos.y) > abs(heightPos.x)) {
        tempLength = heightPos.y;
        heightPos.y = heightPos.x;
        heightPos.x = tempLength;
        tempStep = reorderedStepMotor[1];
        reorderedStepMotor[1] = reorderedStepMotor[0];
        reorderedStepMotor[0] = tempStep;
    }
    if (abs(heightPos.z) > abs(heightPos.x)) {
        tempLength = heightPos.z;
        heightPos.z = heightPos.x;
        heightPos.x = tempLength;
        tempStep = reorderedStepMotor[2];
        reorderedStepMotor[2] = reorderedStepMotor[0];
        reorderedStepMotor[0] = tempStep;
        _z_slantways = true;
    }    
    
    if (solenoidOn) 
        _bmp.openImg("/local/pic.bmp");
    reversing = false;
    enableSteppers(true);
    doLinearSideways(heightPos, basePos, reorderedStepMotor, maxSpeed, solenoidOn);
    if (solenoidOn)
        _bmp.closeImg();
    if (reversing) {
        homePosition.x -= basePos.x;
        homePosition.y -= basePos.y;
        homePosition.z -= basePos.z;
    }
    interpolate(homePosition, maxSpeed);
}

void LinearMotion::doLinearSideways(Vector delta, Vector nextRow,
                     Stepper ** stepMotor, int maxSpeed, bool solenoidOn) {
    int fxy,fxz;
    int rowLoc = 0;
    int delay = _initial_delay;
    int delayPos = 0;
    Vector lastRow = {-nextRow.x, -nextRow.y, -nextRow.z};
    Vector dir = {1, 1, 1};
    long stepsPerPixel;
    _z_slantways ? stepsPerPixel = _z_steps_per_pixel : stepsPerPixel = _steps_per_pixel;
    
    if(delta.x < 0)
        dir.x = 0; //towards motor
    if(delta.y < 0)
        dir.y = 0; //towards motor
    if(delta.z < 0)
        dir.z = 0; //towards motor
    delta.x = abs(delta.x);
    delta.y = abs(delta.y);
    delta.z = abs(delta.z);
    fxy = delta.x - delta.y;
    fxz = delta.x - delta.z;
        
    Vector curPos = {0, 0, 0};
    
    while(!(*_stopped) && (curPos.x<=delta.x) && (curPos.y<=delta.y) && (curPos.z<=delta.z)){
       // printf("Moving height: %d, %d, %d\n\r", curPos.x, curPos.y, curPos.z);
        if ((curPos.x % stepsPerPixel) == 0) {
            Vector * row = NULL;
            if (solenoidOn)
                _bmp.setRow(rowLoc++);
            if (!(solenoidOn && _bmp.isBlankRow())) {
                reversing ? row = &lastRow : row = &nextRow;
                interpolate(*row, maxSpeed, solenoidOn);
                reversing = !reversing;
                enableSteppers(true); // Hacky
            }
        }
        ++curPos.x;
        if ((curPos.x % stepsPerPixel) <= stepsPerPixel/2) {
            delayPos++;
            delay = delayTime(delay, delayPos);
        } else {
            delayPos--;
            delay = delayTime(delay, -delayPos);
        }
        stepMotor[0]->stepOn(dir.x);
        fxy -= delta.y;
        fxz -= delta.z;
        if(fxy <= 0){
            ++curPos.y;
            stepMotor[1]->stepOn(dir.y);
            fxy += delta.x;
        }
        if(fxz <= 0){
            ++curPos.z;
            stepMotor[2]->stepOn(dir.z);
            fxz += delta.x;
        }
        wait_us(1);
        stepMotor[0]->stepOff();
        stepMotor[1]->stepOff();
        stepMotor[2]->stepOff();
        wait_us(delay);
        while(*_paused) {;}
    }
}

void LinearMotion::doLinear(Vector delta, Stepper** stepMotor, int maxSpeed, bool solenoidOn) {
    int fxy,fxz;
    int pixelLoc = 0;
    int delay = _initial_delay;
    int farthestDelay = 0;
    Vector dir = {1, 1, 1};
    long stepsPerPixel;
    _z ? stepsPerPixel = _z_steps_per_pixel : stepsPerPixel = _steps_per_pixel;
    
    if(delta.x < 0)
        dir.x = 0; //towards motor
    if(delta.y < 0)
        dir.y = 0; //towards motor
    if(delta.z < 0)
        dir.z = 0; //towards motor
    delta.x = abs(delta.x);
    delta.y = abs(delta.y);
    delta.z = abs(delta.z);
    fxy = delta.x - delta.y;
    fxz = delta.x - delta.z;
        
    Vector curPos;
    curPos.x = 0;
    curPos.y = 0;
    curPos.z = 0;
    while (!(*_stopped) && (curPos.x<=delta.x)&&(curPos.y<=delta.y)&&(curPos.z<=delta.z)){
        if (solenoidOn) {
            if ((reversing && ((delta.x - curPos.x - stepsPerPixel / _step_buffer) % stepsPerPixel == 0)) ||
               (!reversing && ((curPos.x + stepsPerPixel / _step_buffer) % stepsPerPixel == 0)))
                *_sol = _bmp.isPixel(pixelLoc++, reversing);
            else if ((reversing &&  ((delta.x - curPos.x + stepsPerPixel / _step_buffer) % stepsPerPixel == 0)) ||
                    (!reversing &&  ((curPos.x - stepsPerPixel / _step_buffer) % stepsPerPixel == 0)) )
                *_sol = 0;
        }
        ++curPos.x;
        if (delay > maxSpeed) {
            delay = delayTime(delay, curPos.x);
            farthestDelay = curPos.x;
        } else if (delta.x - curPos.x < farthestDelay) {
            delay = delayTime(delay, -curPos.x);
        }
        stepMotor[0]->stepOn(dir.x);
        fxy -= delta.y;
        fxz -= delta.z;
        if (fxy <= 0){
            ++curPos.y;
            stepMotor[1]->stepOn(dir.y);
            fxy += delta.x;
        }
        if (fxz <= 0){
            ++curPos.z;
            stepMotor[2]->stepOn(dir.z);
            fxz += delta.x;
        }
        wait_us(1);
        stepMotor[0]->stepOff();
        stepMotor[1]->stepOff();
        stepMotor[2]->stepOff();
        wait_us(delay);  //Implement linear accelleration!
        if (*_paused) {
            enableSteppers(false);
            *_sol = 0;
            while(*_paused){printf("Pausing!\n\r");}
            enableSteppers(true);
        }
    }
    *_sol = 0;
}

void LinearMotion::updateSettings(long steps_per_pixel, long initial_delay, long step_buffer) {
    _steps_per_pixel = steps_per_pixel;
    _z_steps_per_pixel = (steps_per_pixel * 8) / 5;
    _step_buffer = step_buffer; // Make a gap of _steps_per_pixel/_step_buffer  between each pixel
    _initial_delay = initial_delay; // in us
} 
      
int LinearMotion::delayTime (int oldDelay, int stepNumber) {
    return oldDelay - (2*oldDelay)/(4*stepNumber + 1);
}

      
void LinearMotion::enableSteppers(bool en) {
    StepMotor[0]->enable(en);
    StepMotor[1]->enable(en);
    StepMotor[2]->enable(en);
}
