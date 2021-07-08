#include <stdio.h>
#include <stdlib.h>
#include "isw_1.h"

// The shares of input_a and input_b and also random numbers are sent through python code.
// Then just the multiplication is done by the Cortex-M3
// and it's corresponding power is measured via PicoScope


/*The number of shares: Mask_order+1: 1+1=2*/
int  share_n = 2;

/*The number of randomness for gadget: ISW: share_n *(share_n - 1)/2 */
// int rnd_gadget = share_n *(share_n - 1)/2;
/*The number of randomness for masking the inputs: 2* Mask_order (share_n - 1)*/
// int rnd_mask_in = 2 * (share_n - 1);
// rnd_gadget
int rnd_n = 1;

int main( int argc, char* argv[]){
    if( !scale_init(&SCALE_CONF)){
        return -1;
    }

    uint8_t rnd[rnd_n];

    uint8_t shares_a[share_n];
    uint8_t shares_b[share_n];
    uint8_t shares_ab[share_n];

    while(true) {
        bool t = scale_gpio_rd( SCALE_GPIO_PIN_GPI);
        scale_gpio_wr( SCALE_GPIO_PIN_GPO, t);


        for (int i = 0; i < share_n; i++) {
            shares_a[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }

        for (int i = 0; i < share_n; i++) {
            shares_b[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }

        for (int i = 0; i < rnd_n; i++) {
            rnd[i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        }

        ///////////////////////////////////////////////////////////////////////////////////////////////////
        ///////////////////////////////////////////////////////////////////////////////////////////////////
        //scale_delay_ms( 0.01 );

        scale_gpio_wr( SCALE_GPIO_PIN_TRG, true  );

        Isw_1(shares_a, shares_b, &(rnd[0]), shares_ab);

        scale_gpio_wr( SCALE_GPIO_PIN_TRG, false );
        //scale_delay_ms( 0.01 );
        ///////////////////////////////////////////////////////////////////////////////////////////////////
        ///////////////////////////////////////////////////////////////////////////////////////////////////

        for (int i = 0; i < share_n; i++) {
            scale_uart_wr(SCALE_UART_MODE_BLOCKING, ((char) shares_ab[i]));
        }



    }
    return 0;
}

