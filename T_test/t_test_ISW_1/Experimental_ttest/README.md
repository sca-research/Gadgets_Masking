### T-test
**AIM**: Performing **leakage Detection** by using **T-test** on
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
   
   
   









while it is executing 
[multiplication gadgets]((https://github.com/sca-research/Gadgets_Masking/tree/main/Assembly_implementation)) written in Assembly Thumb-16 instructions.

Traces are recorded by [Pico oscilloscope 5000a](https://www.picotech.com/products/oscilloscope).

This explanation is related to ISW_1, but it is compatible with other gadgets. 
1. Finding the execution time of the gadget (**pico.png**).
- Programming the [SCALE board](https://github.com/danpage/scale):
  (Please read [this page](https://github.com/sca-research/Gadgets_Masking/tree/main/Assembly_implementation))
  
  **Notice**: in **isw_1.c**, we need to imply some changes to specify 
  which part of signal (just the multiplication) is being to be captured:
  
  After  ```while(true) { ```, adding the below instructions:
  ```
        bool t = scale_gpio_rd( SCALE_GPIO_PIN_GPI);
        scale_gpio_wr( SCALE_GPIO_PIN_GPO, t);
  ```

  And also modifying ```Isw_1(shares_a, shares_b, &(rnd[2]), shares_ab);``` as below:
  ```
        scale_gpio_wr( SCALE_GPIO_PIN_TRG, true);
        Isw_1(shares_a, shares_b, &(rnd[2]), shares_ab);
        scale_gpio_wr( SCALE_GPIO_PIN_TRG, false);
  ```
  In addition, in this set up the order of receiving input b and random numbers are changed. 

- Connecting both **Signal** and **Trigger** of  [SCALE board](https://github.com/danpage/scale)
  to the [Pico oscilloscope 5000a](https://www.picotech.com/products/oscilloscope).
- Running the **test.py**, to send and receive data to/from [SCALE board](https://github.com/danpage/scale)
- Opening the [PicoScope Software](https://www.picotech.com/products/oscilloscope) and measuring the period.

2) Using **acquisition.py** for recording the traces.
  The **acquisition.py**, transfers inputs and outputs between Scale board and PC (like **test.py**),
and enables the PicoScope to stores the corresponding traces.

  - For individual gadget, **Mask_ORD** and **rnd_gadget** have be changed.
  - Regarding the time period of the gadget, **samples** and **timebase** have to be changed.
For example, in case of ISW_1, the period is 20us.
    The clock of Scale board is 12 MHz : period =  1 / 12 MHz = 83.3 ns.
    20us\83.3ns= 240 (the number of clocks for the ISW_1),
    
    Sampling each clock with 40 points: 40 * 240 = 10 K sample (the whole sampling points for  ISW_1).
    Sampling rate: period = 20us, samples = 10Ks: 10K s / 20us = 500 Msample/S.
    timebase = 1 / Sampling rate: 1/500MS = 2 ns, according to the table in AAP5000, timebase for 2ns is 1.
  
