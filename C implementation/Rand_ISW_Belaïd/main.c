#include "stdint.h"
#include "Modified_ISW.h"
#include "stdio.h" //printf
#include "stdlib.h"
#include "time.h"
//////////////////////////////////////////////////////////////////////
int main(void)
{
    time_t t;
    srand((unsigned) time(&t));

    uint8_t a[NUM_SHARES];
    uint8_t b[NUM_SHARES];
    uint8_t operand_a = 0x53;
    uint8_t operand_b = 0x10;
    uint8_t c[NUM_SHARES];

    Mask(a, operand_a);
    Mask(b, operand_b);
    Modified_ISW_MULT(a, b, c);

    printf("Shares of the output:\n");
    for (int i = 0; i < NUM_SHARES; i++)
    {
            printf(" %02x ", c[i]);
    }
}

