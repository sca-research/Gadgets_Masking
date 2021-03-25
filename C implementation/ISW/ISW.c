#include "ISW.h"
#include "stdint.h"
#include "gfmul.h"



void ISW_MULT(uint8_t* a, uint8_t* b, uint8_t* c)
{
    uint8_t r[NUM_SHARES][NUM_SHARES];
    for (int i = 0; i < NUM_SHARES; i++)
    {
        for (int j = i + 1; j < NUM_SHARES; j++)
        {
             r[i][j]= getRand();
            // The order is important
             r[j][i] = (r[i][j] ^ gfMul(a[i], b[j])) ^ gfMul(a[j], b[i]);
        }
    }
    for (int i = 0; i < NUM_SHARES; i++)
    {
        c[i]= gfMul(a[i], b[i]);
        for (int j = 0; j < NUM_SHARES; j++)
        {
            if (i != j)
            {
                c[i] ^=r[i][j];
            }
        }

    }
}
