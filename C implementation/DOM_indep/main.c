/*Here the correctness of the gadget is checked with random inputs (a and b).*/

#include "stdio.h" //printf
#include "stdlib.h" //srand()
#include "time.h"
#include "DOM_Indep.h"

uint8_t gmul(uint8_t a, uint8_t b);

//////////////////////////////////////////////////////////////////////
int main(void)
{
    time_t t;
    srand((unsigned) time(&t));

    for (int i = 0; i < 1000; i++) {
        uint8_t a = rand() % 256;
        uint8_t b = rand() % 256;
        uint8_t c[Mask_ORD + 1];

        DOM_independent(a, b, c);


       // printf("\n  -------------------------Number of shares: %0d", Mask_ORD+1);
/*        for (int i = 0; i <= Mask_ORD; i++) {
            printf(" %02x ", c[i]);
        }*/
        uint8_t output = 0;
        for (int i = 0; i <= Mask_ORD; i++) {
            output ^= c[i];
        }
/*
        printf(" \n a: %02x  \n b: %02x", a, b );
        printf(" \n Unmasked_c = a * b: %02x \n     Mask_c = a * b: %02x ",gfMul(a,b) , output);
*/

        if (output != gmul(a, b)) {
            printf(" \n Error for inputs : a = %02x , b = %02x and Num_shares: %0d \n", a, b, Mask_ORD+1);
        }
        else{
            //printf(" \nMask_c = Unmasked_c \n");

        }
    }
}

// Cite https://en.wikipedia.org/wiki/Finite_field_arithmetic
/*
Multiplication of two numbers (a and b) in the GF(2^8) with the polynomial x^8 + x^4 + x^3 + x + 1
x^8 + x^4 + x^3 + x + 1---> in binary format:10001011 = 11b
*/
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

