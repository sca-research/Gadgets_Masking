#include <basic_math.h>


void Mask(uint8_t* y, uint8_t x)
{
    y[0] = x;
    for(int i = 1; i <= Mask_ORD; i++)
    {
        y[i]=  rand() % 256;
        y[0] = y[0] ^ y[i];
    }
}


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


