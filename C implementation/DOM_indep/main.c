#include "stdio.h" //printf
#include "stdlib.h" //srand()
#include "time.h"
#include "DOM_Indep.h"

//////////////////////////////////////////////////////////////////////
int main(void)
{
    time_t t;
    srand((unsigned) time(&t));

    uint8_t a = 0x20;
    uint8_t b = 0x10;
    uint8_t c[Mask_ORD+1];

    DOM_independent(a, b, c);

    printf("Shares of the output:\n");
    for (int i = 0; i <= Mask_ORD; i++)
    {
        printf(" %02x ", c[i]);
    }
    printf("\n \n The output:\n");
    uint8_t output=0;
    for (int i = 0; i <= Mask_ORD; i++)
    {
        output^=c[i];
    }
    printf(" %02x ", output);
}

