#include <stdio.h>
#include <stdlib.h>

#include "isw_1.h"

uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0; /* the product of the multiplication */
    while (a && b) {
        if (b & 1) /* if b is odd, then add the corresponding a to p (final product = sum of all a's corresponding to odd b's) */
            p ^= a; /* since we're in GF(2^m), addition is an XOR */

        if (a & 0x80) /* GF modulo: if a >= 128, then it will overflow when shifted left, so reduce */
            a = (a << 1) ^ 0x11b; /* XOR with the primitive polynomial x^8 + x^4 + x^3 + x + 1 (0b1_0001_1011) – you can change it but it must be irreducible */
        else
            a <<= 1; /* equivalent to a*2 */
        b >>= 1; /* equivalent to b // 2 */
    }
    return p;
}


/*
The number of shares: Mask_order+1: 1+1=2
*/
int  share_n = 2;

/*
The number of randomness for ISW: Mask_order*(Mask_order + 1)/2: 1*(1+1)/2=1
The number of randomness for masking the inputs: 2* Mask_order: 2*1=2
 Total rnd = 1 + 2 =3
*/
int rnd_n = 3;


/*
The number of randomness for masking the inputs: 2* Mask_order: 2*1=2
*/

/*Masking the inputs: First order---> 2 shares*/
void Mask(uint8_t x, uint8_t rnd, uint8_t* y)
{
    y[0] = rnd;
    y[1] = x ^ rnd;
}

int main( int argc, char* argv[]){
    if( !scale_init(&SCALE_CONF)){
        return -1;
    }

/*rnd_mask_n + rnd_isw_n = 3*/
    uint8_t rnd[rnd_n];

    uint8_t in_a;
    uint8_t in_b;


    uint8_t shares_a[share_n];
    uint8_t shares_b[share_n];
    uint8_t shares_ab[share_n];


    while(true) {
        in_a = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        in_b = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);

        for (int i = 0; i < rnd_n; i++) {
            rnd[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }


        Mask(in_a, (rnd[0]), shares_a);
        Mask(in_b, (rnd[1]), shares_b);
        Isw_1(shares_a, shares_b, &(rnd[2]), shares_ab);

        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) in_a));
        for (int i = 0; i < 2; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_a[i]));
        }
        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) in_b));
        for (int i = 0; i < 2; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_b[i]));
        }

        for (int i = 0; i < 2; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_ab[i]));
        }
        //
        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) gmul(in_b, in_a)));


    }
    return 0;
}