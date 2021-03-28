#include "stdint.h"
// The number of shares used for masking
#define NUM_SHARES 2

void Mask(uint8_t y[NUM_SHARES], uint8_t x);

uint8_t getRand(void);
