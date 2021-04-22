/*Here the correctness of the gadget is checked with random inputs (a and b).*/
#include "Opt_Ref_Mask.h"

void Mask(uint8_t* y, uint8_t x);
int rnd_number(int Mask_order);
//////////////////////////////////////////////////////////////////////
int main(void)
{

    //////////////////////////////////////////////////////////////////////
    time_t t;
    srand((unsigned) time(&t));

    for (int n = 0; n < 1; n++) {

        // random inputs
        uint8_t input_a = rand() % 256;
        uint8_t mask_in[Mask_ORD+1];
        uint8_t d[Mask_ORD + 1];

        // Random number: on_the_fly
        int rnd_n = 0;
        rnd_n = rnd_number(Mask_ORD);
        printf("\n rnd %0d", rnd_n);

        uint8_t rnd_f[rnd_n];
        for (int k = 0; k <rnd_n; k++){
            rnd_f[k] = rand() % 256;
            //printf( "  %02x  ", rnd_f[k]);
        }

       /* kOpt_Ref_Mask two vectors of randomness, one for r and one sor s0 (s1)
        The length of vectors:
        s0: d (Mask_ORD +1) elements (randomness)
        r : (rnd_n - d) elements (randomness)
*/


        Mask(mask_in, input_a);

        // Calling the Optimized RefreshMasks
        opt_refresh_mask(mask_in, Mask_ORD, rnd_f, d);


        // Verifying the Optimized RefreshMasks
        uint8_t output = 0;
        for (int i = 0; i <= Mask_ORD; i++) {
            output ^= d[i];
            //printf("\n d%0d: %02x", i,d[i]);

        }
        printf("\nOUT %02x", output);

        printf("\nin %02x", input_a);
        if(output != input_a){
            printf("\n!!!!!!!!!!!!!!!!!! ERROR:Not equal\n");
        }
        printf("\n++++++++++++++++++++++\n");


    }
}

void Mask(uint8_t* y, uint8_t x)
{
    y[0] = x;
    for(int i = 1; i <= Mask_ORD; i++)
    {
        y[i]=  rand() % 256;
        y[0] = y[0] ^ y[i];
    }
}

// The number of randomness in Optimized RefreshMask
int rnd_number(int Mask_order){
    int d = Mask_order+1;

    if (d <= 3){
        return (d-1);
    }

    if (d <= 5){
    return d;
    }

    if (d <=11){
    return (2*d -5);
    }

    if (d ==12){
    return (d+8);
    }

    if (d <=16){
        return (2*d);
    }
}