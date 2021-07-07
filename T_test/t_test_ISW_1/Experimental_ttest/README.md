### T-test on real power traces

In this case, power traces are needed.

The power of 32-bit ARM Cortex-M0/3 microprocessor is
captured while it is executing 
**Multiplication Gadget**.

Regarding the experimental setup which is considered,
several steps have to be performed.
1) Compiling the **Multiplication Gadget** file as
   the source code for ARM cortex-M0/3 to an 
   executable one, and running the executable file on that.
   
2) Communication with the ARM cortex-M0/3, in order
   to send fixed and random inputs.
   
3) Measuring the power traces of Microprocessor while it is
   running the executable file. It is better if Triggers are used 
   to specifying the start and the end of the gadget.
   
4) Performing T-test on recorded traces.



### Summery of files:

**test.py**: Checking the correctness of the gadget.

**acquisition.py**: Transferring data between Microcontroller and Pc,
and capturing the power in trs file via oscilloscope.

**analysis_trs.py**: For analysing the data and powers.

**t_test.py**: performing T-test.






 
