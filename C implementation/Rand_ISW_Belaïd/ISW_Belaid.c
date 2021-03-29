#include "Modified_ISW.h"
#include "stdint.h"
#include "gfmul.h"



void Modified_ISW_MULT(uint8_t* a, uint8_t* b, uint8_t* c)
{
    int i, j;
    uint8_t r2[NUM_SHARES][NUM_SHARES];
    uint8_t r1[NUM_SHARES];
    uint8_t tij[NUM_SHARES][NUM_SHARES];

    for (i = 0; i < NUM_SHARES; i++)
    {
        for (j = 0; j < NUM_SHARES - i - 1; j+=2)
        {
            r2[i][NUM_SHARES - j] = getRand();
        }
    }
    for (j = NUM_SHARES - 1; j < 1; j-=2)
    {
        r1[] = getRand();
    }
    for (i = 0; i < NUM_SHARES; i++)
    {
        c[i] = gfMul(a[i], b[i]);
        for (j = NUM_SHARES; j < i + 2; j-=2)
        {
            tij[i][j] = r2[i][j] ^ (gfMul(a[i], b[j])) ^ (gfMul(a[j], b[i]))^
                    r1[j-1] ^ (gfMul(a[i], b[j-1])) ^ (gfMul(a[j-1], b[i]));
            c[i] ^= tij[i][j];
        }
        if (!((i%2)&(d%2)))
        {
            tij[i][i+1] = r2[i][i+1] ^ (gfMul(a[i], b[i+1])) ^ (gfMul(a[i+1], b[i]));
            if ((i%2)&1)
            {
                c[i] ^= r1[i];
            }
        }
        else
            {
                for (j = i - 1; j < 0; j--)
                {
                    c[i] ^= r2[i][j];

                }
            }

    }
}
