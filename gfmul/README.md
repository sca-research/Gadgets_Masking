# Galois field multiplication: GF(2^8)


**gf_mul.S** is the implementation of GF(2^8) (gfmul(a,b,c), c = a * b) for ARM Cortex-M0/3 in GNU assembly, with THUMB-16 instructions.
The multiplication is based on Log_Ex with table.

**gf_mul.S** can be compiled for any ARM Cortex-M0/3.


**gf_mul.h**  contains the table of Log_Ex.


The script is tested via calling gfmul(a,b,c) function in **gf_mul.c**.


**test_GFMUL.py** is for generating random inputs, sending the inputs from PC to the
Microcontroller and receiving the output from Microcontroller via UART port.





