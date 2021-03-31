#include "stdint.h"
#include "stdlib.h" //rand()
#include "ISW_Belaid.h"

static uint8_t a[Mask_ORD+1];
static uint8_t b[Mask_ORD+1];

uint8_t gfMul(uint8_t a, uint8_t b)
{
    int s = 0;
    s = table[a] + table[b];
    int q;
    /* Get the antilog */
    s = table[s+256];
    uint8_t z = 0;
    q = s;
    if(a == 0) {
        s = z;
    } else {
        s = q;
    }
    if(b == 0) {
        s = z;
    } else {
        q = z;
    }
    return s;
}

    void Mask(uint8_t y[Mask_ORD+1], uint8_t* x)
    {
        y[0] = x;
        for(int i = 1; i <= Mask_ORD; i++)
        {
            y[i]=  rand() % 256;
            y[0] = y[0] ^ y[i];
        }
    }

    void Refresh_Mask(uint8_t y[Mask_ORD+1], uint8_t x[Mask_ORD+1])
    {
        uint8_t tmp;
        for (int i = 1; i <= Mask_ORD; i++) {
            tmp = rand() % 256;
            y[0] = x[0] ^ tmp;
            y[i] = x[i] ^ tmp;
        }
    }


    void ISW_Belaid_MULT(uint8_t* input_a, uint8_t* input_b, uint8_t* c)
    {
        Mask(a, input_a);
        Mask(b, input_b);
        Refresh_Mask(a,a);
        Refresh_Mask(b,b);
        int i, j;
        uint8_t r2[Mask_ORD+1][Mask_ORD+1];
        uint8_t r1[Mask_ORD+1];
        uint8_t temp[Mask_ORD+1][Mask_ORD+1];

        for (i = 0; i <= Mask_ORD; i++)
        {
            for (j = 0; j <= Mask_ORD-i-1; j+=2)
            {
                r2[i][Mask_ORD-j] = rand() % 256;
            }
        }
        for (j = Mask_ORD-1; j >= 1; j-=2)
        {
            r1[j] = rand() % 256;
        }
        for (i = 0; i <=Mask_ORD; i++)
        {
            c[i] = gfMul(a[i], b[i]);
            for (j = Mask_ORD; j >= i + 2; j-=2)
            {
                temp[i][j] = r2[i][j] ^ (gfMul(a[i], b[j])) ^ (gfMul(a[j], b[i]))^
                            r1[j-1] ^ (gfMul(a[i], b[j-1])) ^ (gfMul(a[j-1], b[i]));
                c[i] ^= temp[i][j];
            }
            if (!((i%2)&((Mask_ORD)%2))) //(i%2) != (NUM_SHARES%2)
            {
                temp[i][i+1] = r2[i][i+1] ^ (gfMul(a[i], b[i+1])) ^ (gfMul(a[i+1], b[i]));
                c[i] ^=temp[i][i+1];
                if ((i%2)&1)
                {
                    c[i] ^= r1[i];
                }
            }
            else
            {
                for (j = i-1; j >= 0; j--)
                {
                    c[i] ^= r2[j][i];

                }
            }

        }
    }
