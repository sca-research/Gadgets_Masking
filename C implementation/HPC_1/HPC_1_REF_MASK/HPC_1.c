
/*
 HPC_1: Fig.2 (c)  in "Hardware Private Circuits: From Trivial Composition to Full Verification"
*/
#include "basic_math.h"
#include "HPC_1.h"
#include "Ref_Mask.h"
#include "DOM_Indep.h"
#include "string.h" // memcpy func
/*
    hpc1(INPUT: input_a[Mask_ORD+1], INPUT: input_b[Mask_ORD+1], INPUT: uint8_t* rnd_Ref,INPUT: uint8_t * rnd_DOM, OUTPUT: c[Mask_ORD+1])
    c = a * b
    * works for any field : this program is for field: 2^3=8
    *
        rnd_DOM: Mask_ORD * (Mask_ORD+1) /2;
        rnd_Ref: Func --> ((Mask_ORD+1) * log(Mask_ORD+1));
        */

////////////////////////////////////////////////

 void hpc1(uint8_t* input_a, uint8_t* input_b, uint8_t* rnd_Ref, uint8_t * rnd_DOM, uint8_t* c) {
    int i, j;

    static uint8_t share_0_mask[Mask_ORD + 1]; // The output of refresh_mask
    static uint8_t add_inb_share0[Mask_ORD + 1]; // Adding input_b and share_0_mask
    static uint8_t input_b_Ref[Mask_ORD + 1]; // Register for the output of adding input_b and share_0_mask


    /*Refresh part:*/
    ////////////////////////////////////////////////////////////////////
    uint8_t all_zero_input[Mask_ORD+1] = {0x00};

    refresh_mask(all_zero_input, 0, Mask_ORD,  rnd_Ref, share_0_mask);

    for (int i = 0; i <= Mask_ORD; i++) {
        add_inb_share0[i] = input_b[i] ^ share_0_mask[i];
    }
    memcpy(input_b_Ref, add_inb_share0, sizeof add_inb_share0);


    /*Multiplication part:*/
    ////////////////////////////////////////////////////////////////////
    DOM_independent(input_a, input_b_Ref, rnd_DOM, c);
}



