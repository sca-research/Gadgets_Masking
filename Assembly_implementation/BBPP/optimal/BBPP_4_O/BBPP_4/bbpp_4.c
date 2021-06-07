#include <stdio.h>
#include <stdlib.h>
#include "bbpp_4.h"

void Mask(uint8_t x, uint8_t* rnd, uint8_t* y);
uint8_t gmul(uint8_t a, uint8_t b);

/*The number of shares: Mask_order+1: 4+1=5*/
int  share_n = 5;

/*The number of randomness for BBPP_": 5
The number of randomness for masking the inputs: 2* Mask_order: 2*4=8
 Total rnd = 5 + 5 =13*/
//int rnd_n = 13;

int main( int argc, char* argv[]){
    if( !scale_init(&SCALE_CONF)){
        return -1;
    }

    uint8_t rnd_a[share_n - 1];
    uint8_t rnd_b[share_n - 1];
    uint8_t rnd_bbpp[5];

    uint8_t in_a;
    uint8_t in_b;

    uint8_t shares_a[share_n];
    uint8_t shares_b[share_n];
    uint8_t shares_ab[share_n];


    while(true) {
        in_a = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        in_b = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);

        for (int i = 0; i < share_n -1 ; i++) {
            rnd_a[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }
        for (int i = 0; i < share_n -1; i++) {
            rnd_b[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }
        for (int i = 0; i < 5; i++) {
            rnd_bbpp[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }

        Mask(in_a, rnd_a, shares_a);
        Mask(in_b, rnd_b, shares_b);
        Bbpp_4(shares_a, shares_b, rnd_bbpp, shares_ab);

        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) in_a));

        for (int i = 0; i < share_n; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_a[i]));
        }

        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) in_b));

        for (int i = 0; i < share_n; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_b[i]));
        }

        for (int i = 0; i < share_n; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_ab[i]));
        }

        scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) gmul(in_b, in_a)));

    }
    return 0;
}

// This function is for checking (c=a*b) ? (c0+c1)
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

/*Masking the inputs: First order---> 4 shares*/
void Mask(uint8_t x, uint8_t* rnd, uint8_t* y)
{
    y[0] = rnd[0];
    y[1] = rnd[1];
    y[2] = rnd[2];
    y[3] = rnd[3];
    y[4] = x ^ (rnd[0] ^ rnd[1] ^ rnd[2] ^ rnd[3]);
}
