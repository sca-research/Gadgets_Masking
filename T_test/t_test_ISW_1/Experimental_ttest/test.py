import serial
import os
from time import sleep
import secrets
import sys

Mask_ORD = 1

step = 10


def masking(x):
    """ This function masks the input x, the type of the output is bytearray"""
    y = bytearray(Mask_ORD + 1)
    rnd = bytearray([secrets.randbits(8) for j in range(0, Mask_ORD + 1)])
    y[Mask_ORD] = x
    for i in range(0, Mask_ORD):
        y[i] = rnd[i]
        y[Mask_ORD] ^= rnd[i]
    return y


def gf_mult(a, b):
    """ Multiplication in the Galois field GF(2^8) """
    p = 0  # The product of the multiplication
    over_f = 0
    for i in range(8):
        # if b is odd, then add the corresponding a to p (final product = sum of all a's corresponding to odd b's)
        if b & 1 == 1:
            p ^= a  # since we're in GF(2^m), addition is an XOR

        over_f = a & 0x80
        a <<= 1
        if over_f == 0x80:
            a ^= 0x1b  # GF modulo: if a >= 128, then it will overflow when shifted left, so reduce
        b >>= 1
    return p % 256


def uart(ser_port, num_repeat):
    """ This function enables the serial_port, and transmits tx_data
        from the PC to the device connected with the PC and receives
        rx_data from the device to the PC. Also it repeats the TX and RX
        transactions num_repeat times"""

    # The length of the TX data in Byte (B)
    # For each gadget, just change Mask_ORD and n_rnd_gadget
    # Here the shares of input_a and input_b are computed, so that
    # The TX data is: mask_a (shares_a), mask_b (shares_b) and n_rnd_gadget
    ##################################################
    # main_inputs = 2  # input_a: 1B, input_b: 1B

    # (Mask_ORD+1) B for shares of input_a, (Mask_ORD+1) B for shares of input_b
    n_shares_input = 2 * (Mask_ORD + 1)
    n_rnd_gadget = int(Mask_ORD * (Mask_ORD + 1) / 2)  # The number of randomness needed in gadget
    input_len_gadget = n_shares_input + n_rnd_gadget

    # The length of the RX data in Byte (B)
    ##################################################
    output_len = (Mask_ORD + 1)  # output_len = shares of c (c = a * b)
    print("Output length: ", output_len)
    print("Input length:  ", input_len_gadget)

    # Enabling the serial port
    ##################################################
    serial_p = serial.Serial(ser_port)

    if serial_p.is_open:
        print("\n ********************* START ********************* \n")

    for i in range(num_repeat):

        # Generating random inputs and randomness (a, b, r)
        # input_a and input_b are sampled in "int" type for
        # being convince to use in masking function and gf_mult function

        input_a = secrets.randbits(8)  # type: int
        input_b = secrets.randbits(8)  # type: int

        # Converting input_a and input_b to "byte" type, in order to storing in trs file
        in_a = input_a.to_bytes(1, sys.byteorder)
        in_b = input_b.to_bytes(1, sys.byteorder)

        # Masking inputs
        mask_a = masking(input_a)  # type: bytearray
        mask_b = masking(input_b)  # type: bytearray

        # Randomness needed in gadget
        rnd_gadget = bytearray([secrets.randbits(8) for j in range(0, n_rnd_gadget)])

        # The input data
        inputs_of_gadget = mask_a + mask_b + rnd_gadget

        # Check
        if len(inputs_of_gadget) != input_len_gadget:  # length in bytes
            print("ERROR INPUT LENGTH")


        # Wait
        # tx: Transmitting input data serially from the PC to the SCALE_Board by UART Serial Port
        sleep(0.08)
        serial_p.write(inputs_of_gadget)

        # rx: Receiving output data serially from the SCALE_Board to the PC  by UART Serial Port
        output = bytearray(serial_p.read(output_len))

        # Checking the correctness of the gadget and printing on the screen
        #################################################
        shares_c = output[0: Mask_ORD + 1]

        out_c = 0
        for p in range(0, Mask_ORD + 1):
            out_c ^= shares_c[p]

        # Checking the output of gadget with the output of gf_mult
        if gf_mult(input_a, input_b) != out_c:
            print("ERROR: gmul(in_b, in_a) != output of gadget")
            break
        # Printing the data on screen after "step" times executions
        if i % step == 0:
            print('- output {}: [{}]'.format(i, output.hex()))
            print('- a: {} ---> shares_a: [{}]'.format(in_a.hex(), mask_a.hex()))
            print('- b: {} ---> shares_b: [{}]'.format(in_b.hex(), mask_b.hex()))
            print('- c: {} ---> shares_c:[{}]'.format(hex(out_c), output.hex()))
            print('- gfm: {}'.format(hex(gf_mult(input_a, input_b))))
            print('___________________________________________________________________')

    print('Serial port: {}'.format(serial_p.name))
    print('___________________________________________________________________')

    # Disabling the serial port
    serial_p.close()

    if not serial_p.is_open:
        print("\n ********************* END ********************* \n")

    return


if __name__ == '__main__':
    serial_port = '/dev/ttyUSB0'

    # The number of running the program
    num = 100000
    uart(serial_port, num)
