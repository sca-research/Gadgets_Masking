#include "stdint.h"
#include "masked.h"
#include "stdlib.h"
#include "stdio.h" //printf

void Mask(uint8_t y[NUM_SHARES], uint8_t x)
{
    y[0] = x;
    for(int i = 1; i < NUM_SHARES; i++)
    {
        y[i]= getRand();
        y[0] = y[0] ^ y[i];
    }
}


uint8_t getRand(void) {
    // This should be replace with actual random number generator
    return rand() % 256;
}