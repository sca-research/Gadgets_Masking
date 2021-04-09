#include "stdint.h"
#include "stdlib.h" //rand()
#include "PINI_2.h"
#include "stdio.h" //printf


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


    void pini_2(uint8_t* input_a, uint8_t* input_b, uint8_t* c) {
        Mask(a, input_a);
        Mask(b, input_b);

        int i, j;

        uint8_t r1[Mask_ORD + 1];
        uint8_t s1[Mask_ORD + 1];
        uint8_t r2[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t s2[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t p0[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t p1[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t p2[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t p3[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t c2[Mask_ORD + 1][Mask_ORD + 1];
        uint8_t t[Mask_ORD + 1][Mask_ORD + 1];


        for (i = 0; i < Mask_ORD + 1; i++) {
            s1[i] = rand() % 256;
            for (j = 0; j < Mask_ORD-i-1; j += 2) {
                r2[i][Mask_ORD - j] = rand() % 256;
            }
        }

        for (j = Mask_ORD - 1; j >= 1; j -= 2) {
            r1[j] = rand() % 256;
        }


        for (i = 0; i < Mask_ORD + 1; i++) {
            for (j = i + 1; j < Mask_ORD + 1; j++) {
                s2[i][j] = s1[i] ^ s1[j];
                p0[i][j] = gfMul(a[i], s2[i][j]);
                p1[i][j] = gfMul(a[i], (b[j] ^ s2[i][j]));
                p2[i][j] = gfMul(b[i], s2[i][j]);
                p3[i][j] = gfMul(b[i], (a[j] ^ s2[i][j]));
            }

            c2[i][Mask_ORD] = gfMul(a[i], b[i]);

            for (j = Mask_ORD; j >= i + 2; i -= 2) {
                t[i][j] = r2[i][j] ^ p0[i][j] ^ p1[i][j] ^ p2[i][j] ^ p3[i][j] ^
                          r1[j - 1] ^ p0[i][j - 1] ^ p1[i][j - 1] ^ p2[i][j - 1] ^ p3[i][j - 1];

                //Ensure:
/*                if ((t[i][j]) == ((r2[i][j]) ^ gfMul(a[i], b[j]) ^ gfMul(a[j], b[i]) ^
                                  (r1[j - 1]) ^ gfMul(a[i], b[j - 1]) ^ gfMul(a[j - 1], b[i]))) {
                    continue;
                } else {
                    printf("  ERROR:i,j: %0d,%0d ", i, j);
                    break;
                }*/

                c2[i][j - 2] = c2[i][j] ^ t[i][j];
            }
            if ((i % 2) != (Mask_ORD % 2)) {
                t[i][i + 1] = r2[i][i + 1] ^ p0[i][i + 1] ^ p1[i][i + 1] ^ p2[i][i + 1] ^ p3[i][i + 1];
                c2[i][i] = c2[i][i + 1] ^ t[i][i + 1];

                if ((i % 2) & 1) {
                    c2[i][0] = c2[i][i] ^ r1[i];
                } else {
                    c2[i][0] = c2[i][i];
                }

            } else {
                for (j = i - 1; j >= 0; j--) {
                    c2[i][j] = c2[i][j + 1] ^ r2[j][i];
                }
            }
            c[i] = c2[i][0];
        }
    }