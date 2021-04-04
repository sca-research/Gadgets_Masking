#include "stdint.h"
#include "stdlib.h" //rand()
#include "DOM_Indep.h"

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


    void DOM_independent(uint8_t* input_a, uint8_t* input_b, uint8_t* c)
    {
        Mask(a, input_a);
        Mask(b, input_b);
        
        int i, j, k;

        if (Mask_ORD % 2 == 0)
        {
            k = j;
        }
        else
        {
            k = (i + j) % 2;
        }

        int randoms = Mask_ORD * (Mask_ORD+1)/2;
        uint8_t r[randoms];
        uint8_t cross_domain[randoms];

        for (i = 0; i < randoms; i++)
        {
            r [i]= rand() % 256;
        }

        for (i = 0; i < Mask_ORD+1; i++) {
            for (j = 0; j < Mask_ORD + 1; j++) {
                int p = (Mask_ORD + 1) * i + j;
                if (i != j) {
                    cross_domain[p] = (gfMul(a[i], b[j])) ^ r[k];
                }
            }
        }

            for (i = 0; i < Mask_ORD+1; i++)
            {
                c[i]= gfMul(a[i], b[i]);

                for (j = 0; j < Mask_ORD+1; j++)
                {
                    int p = (Mask_ORD + 1) * i + j;
                    if (i != j)
                    {
                        c[i] ^=cross_domain[p];
                    }
                }

            }
    }
