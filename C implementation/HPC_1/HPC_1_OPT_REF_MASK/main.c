/*Here the correctness of the gadget is checked with random inputs (a and b).*/
#include "HPC_1.h"
#include "basic_math.h"
#include "stdio.h" //printf
#include "stdlib.h" //srand()
#include "time.h"

uint8_t gmul(uint8_t a, uint8_t b);

//////////////////////////////////////////////////////////////////////
int main(void) {
    time_t t;
    srand((unsigned) time(&t));

    for (int n = 0; n < 1000; n++) {

        // Different and random inputs
        uint8_t input_a = rand() % 256;
        uint8_t input_b = rand() % 256;

        // Input shares of the Gadget (a=a_0,a_1,...,a_d and b=b_0,b_1,...,b_d)
        uint8_t mask_in_a[Mask_ORD + 1];
        uint8_t mask_in_b[Mask_ORD + 1];

        // Output of the Gadget is d_0, d_1, ..., d_d such that d_0 + d_1 + ... + d_d = c (c=a*b)
        uint8_t d[Mask_ORD + 1];

        // Random number: on_the_fly
//////////////////////////////////////////////////////////////////////////////////
/*      Number of randomness:
        DOM_indep: Mask_ORD * (Mask_ORD+1) /2;
        Opt_Ref_Mask: Func --> rnd_number(int Mask_order);
        Total randoms in HPC_1: rnd_n(DOM_indep) + rnd_number(int Mask_order)
                                = (Mask_ORD * (Mask_ORD+1) /2) + rnd_number(Mask_ORD)
        */
        // Number of randomness for Opt_Ref_Mask: Func --> rnd_number(int Mask_order);
        int rnd_n_ORM = rnd_number(Mask_ORD);
        uint8_t rnd_f_ORM[rnd_n_ORM];
        for (int k = 0; k < rnd_n_ORM; k++) {
            rnd_f_ORM[k] = rand() % 256;
            //printf( "  %02x  ", rnd_f_ORM[k]);
        }

        // Number of randomness for DOM_indep --> Mask_ORD * (Mask_ORD+1) /2
        int rnd_n_DOM = Mask_ORD * (Mask_ORD + 1) / 2;

        uint8_t rnd_f_DOM[rnd_n_DOM];
        for (int k = 0; k < rnd_n_DOM; k++) {
            rnd_f_DOM[k] = rand() % 256;
            //printf( "  %02x  ", rnd_f_DOM[k]);
        }
//////////////////////////////////////////////////////////////////////////////////
        // Input shares of the Gadget (a=a_0,a_1,...,a_d and b=b_0,b_1,...,b_d)
        Mask(mask_in_a, input_a);
        Mask(mask_in_b, input_b);

        // Calling the HPC_1 gadget
        hpc1(mask_in_a, mask_in_b, rnd_f_ORM, rnd_f_DOM, d);


        // Verifying the gadget
        uint8_t output = 0;
        for (int i = 0; i <= Mask_ORD; i++) {
            output ^= d[i];
           // printf("\n d%0d: %02x", i, d[i]);
        }
        //printf("\nOUT  %02x", output);
        //printf("\ngmul %02x", gmul(input_a, input_b));
        //printf(" \n  a = %02x , b = %02x and Num_shares: %0d \n", input_a, input_b, Mask_ORD + 1);

        if (output != gmul(input_a, input_b)) {
            printf(" \n Error: a = %02x , b = %02x and Num_shares: %0d \n", input_a, input_b, Mask_ORD + 1);
            break;
        }
        else {
            printf(" CORRECT ");
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
            if (b &
                1) /* if b is odd, then add the corresponding a to p (final product = sum of all a's corresponding to odd b's) */
                p ^= a; /* since we're in GF(2^m), addition is an XOR */

            if (a & 0x80) /* GF modulo: if a >= 128, then it will overflow when shifted left, so reduce */
                a = (a << 1) ^
                    0x11b; /* XOR with the primitive polynomial x^8 + x^4 + x^3 + x + 1 (0b1_0001_1011) – you can change it but it must be irreducible */
            else
                a <<= 1; /* equivalent to a*2 */
            b >>= 1; /* equivalent to b // 2 */
        }
        return p;
    }
