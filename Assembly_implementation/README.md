# Arm assembly (thumb-16 instructions)  for Cortex-M3  



**Each file**: The implementation of the d-Order multiplication (gadget) in Arm assembly, with THUMB-16 instructions.

**main.c** is for testing the multiplication function.

**test_i.py**: Transfering data through UART to/from the [SCALE board](https://github.com/danpage/scale).


For more clarification, please see [C implementation](https://github.com/sca-research/Gadgets_Masking)


Testing: (Example with ISW_1)

Download [SCALE](https://github.com/danpage/scale). Through the terminal:

`git clone http://www.github.com/danpage/scale.git`

`cd scale ; export SCALE="${PWD}"`

`git submodule update --init --recursive `

Copy  [ISW/ISW_1_o/ISW_1/ file](https://github.com/sca-research/Gadgets_Masking/tree/main/Assembly_implementation/ISW/ISW_1_o/ISW_1)
in `scale/hw` directory.
Then:

`cd scale`

`export SCALE="${PWD}"`

`cd hw`

`export SCALE_HW="${PWD}"`

`export TARGET="${SCALE_HW}/target/lpc1313fbd48"`

`cd ${TARGET}`

`make --no-builtin-rules clean all`

`cd ${SCALE_HW}/ISW_1`

`sudo  make --no-builtin-rules -f ${TARGET}/build/lib/scale.mk BSP="${TARGET}/build" USB="/dev/ttyUSB0" PROJECT="isw_1" PROJECT_SOURCES="isw_1.c isw_1.S" clean all program`

or

Copy the **run.sh** file in `scale/hw` directory and via terminal run **./run.sh ISW_1 isw_1**.




Then, on the [SCALE board](https://github.com/danpage/scale):

1) Press and hold the (right-hand) GPI switch,

2) Press and hold the (left-hand) reset switch,

3) Release the (left-hand) reset switch,

4) Transfer via lpc21isp starts,

5) Release the (right-hand) GPI switch,

Finally, running the **test.py**.
