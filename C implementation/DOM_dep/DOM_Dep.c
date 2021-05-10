//DOM-dep
#include "stdint.h"
#include "stdlib.h" //rand()
#include "DOM_Dep.h"

static uint8_t a[Mask_ORD+1];
static uint8_t b[Mask_ORD+1];

    void Mask(uint8_t y[Mask_ORD+1], uint8_t* x){
        y[0] = x;
        for(int i = 1; i <= Mask_ORD; i++){
            y[i]=  rand() % 256;
            y[0] = y[0] ^ y[i];
        }
    }

    void sum_vect(uint8_t in_vect[Mask_ORD+1], uint8_t sum)
    {
        for(int i=1; i< Mask_ORD+1; i++){
            sum += in_vect[i];
        }
    }

    void DOM_independent(uint8_t* input_a, uint8_t* input_b, uint8_t* c){

        int i, j;
        int all_terms = Mask_ORD * (Mask_ORD+1)/2;
        uint8_t r[all_terms];
        uint8_t reg[2*all_terms];

        for (i = 0; i < all_terms; i++){
            r [i]= rand() % 256;
        }
        for (i = 0; i < Mask_ORD + 1; i++){
            uint8_t output = 0;
            for (j = 0; j < Mask_ORD + 1; j++){
                int p = (Mask_ORD + 1) * i + j;
                if (i == j){
                    output = output ^  gfMul(input_a[i],input_b[j]);
                }
                if (j > i){
                    reg[p] = (gfMul(input_a[i], input_b[j])) ^ r[i + (j*(j-1)/2)];
                }
                else{
                    reg[p] = (gfMul(input_a[i], input_b[j])) ^ r[j + (i*(i-1)/2)];
                }
                if (i!=j){

                    output = output ^ reg[p];
                }
            }
            c[i] = output;
        }

    }




    void DOM_dependent(uint8_t* input_a, uint8_t* input_b, uint8_t* c)
    {
        int i;
        uint8_t x_sum;
        Mask(a, input_a);
        Mask(b, input_b);

        uint8_t out_Dom_ind[Mask_ORD+1];
        uint8_t z[Mask_ORD+1];
        uint8_t x[Mask_ORD+1];

        for (i = 0; i < Mask_ORD+1; i++){
            z[i] = rand() % 256;
            x[i] = b[i] ^ z[i];
        }

        sum_vect(x, x_sum);
        DOM_independent(a, b, out_Dom_ind);

        for (i = 0; i < Mask_ORD+1; i++){
            c[i] = out_Dom_ind[i] ^ (gfMul(a[i] , x_sum));
        }

    }
/* uint8_t gfMul(uint8_t a, uint8_t b)
    {
        int s = 0;
        s = table[a] + table[b];
        int q;
        *//* Get the antilog *//*
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
    }*/

uint8_t gfMul(uint8_t a, uint8_t b)
{
    int s = 0;
    s = table[a] + table[b];
    /* Get the antilog */
    s = table[s+256];
/*
    Checking a=0 or b=0, without conditional branch: if (a==0 or b==0){return 0;} else{return s;}
     Countermeasure for Power analysis attacks
*/
    uint8_t tmp = 0;
    tmp = b & (-a >> 8);
    s = s & (-tmp >> 8);
    return s;
}
