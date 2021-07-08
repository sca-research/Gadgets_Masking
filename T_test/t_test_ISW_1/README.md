### T-test
**AIM**: Decreasing the leakage points in T_test for ISW_1 


**leakage Detection** is carried out by using **T-test** on
"Multiplication gadgets" (writen for ARM cortex-M0/3 in
GNU Assembly with THUMB-16 instructions,
[this page](https://github.com/sca-research/Gadgets_Masking/tree/main/Assembly_implementation)).

There are two **T-test**s:
1) **T-test** is applied on real power traces.
   This means, while "multiplication gadget" is executing on ARM cortex-M0/3,
   the corresponding traces are recorded by an oscilloscope.
   In this experiment, in order to reduce the physical effects of the device, 
   the capturing is carried out randomly.
   Please see **acquisition.py**.
   
2) **T-test** based on simulated power traces.
   In this setup, [GILES](https://github.com/sca-research/GILES) 
   is used to simulating the power traces.
   
