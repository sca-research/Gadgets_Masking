import serial
import os
from time import sleep


def uart(ser_port, num_repeat):
    """ This function enables the serial_port, and transmits tx_data
        from the PC to the device connected with the PC and receives
        rx_data from the device to the PC. Also it repeats the TX and RX
        transactions num_repeat times"""

    # The length of the TX data in Byte (B)
    # For each gadget, just change Mask_ORD and rnd_gadget
    ##################################################
    Mask_ORD = 2
    main_inputs = 2  # input_a: 1B, input_b: 1B
    rnd_masking_inputs = 2 * Mask_ORD  # Mask_ORD B randomness for masking a, Mask_ORD B randomness for masking b
    rnd_gadget = int(Mask_ORD * (Mask_ORD + 1) / 2)  # ISW_2 multiplication
    input_len = main_inputs + rnd_masking_inputs + rnd_gadget

    # The length of the RX data in Byte (B)
    ##################################################
    # output_len = input_a and input_b + shares of input_a, input_b and output_c + gfMUL(a,b)
    output_len = main_inputs + 3 * (Mask_ORD + 1) + 1  # byte length of output_c: Mask_ORD + 1 (c = a * b)
    print("Output length: ", output_len)
    print("Input length:  ", input_len)

    # Enabling the serial port
    ##################################################
    serial_p = serial.Serial(ser_port)

    if serial_p.is_open:
        print("\n ********************* START ********************* \n")

    for i in range(num_repeat):

        # Generating random inputs and randomness (a, b, r)
        inputs = os.urandom(input_len)

        # Wait
        # tx: Transmitting input data serially from the PC to the SCALE_Board by UART Serial Port
        sleep(0.08)
        serial_p.write(inputs)

        # rx: Receiving output data serially from the SCALE_Board to the PC  by UART Serial Port
        output = serial_p.read(output_len)

        # Checking the correctness of the gadget and printing on the screen
        #################################################
        in_a = output[0]
        in_b = output[1]
        shares_a = output[2:Mask_ORD + 3]
        shares_b = output[Mask_ORD + 3: 2 * Mask_ORD + 4]
        shares_ab = output[2 * Mask_ORD + 4: 3 * Mask_ORD + 5]
        gmul = output[3 * Mask_ORD + 5]

        a = 0
        b = 0
        ab = 0  # ab = a * b = c
        for p in range(0, Mask_ORD + 1):
            ab ^= shares_ab[p]
            a ^= shares_a[p]
            b ^= shares_b[p]

        if a != in_a:
            print("ERROR: XOR(shares_a)!=in_a")
            break
        if b != in_b:
            print("ERROR: XOR(shares_b)!= in_b")
            break
        if gmul != ab:
            print("ERROR: XOR(shares_ab)!= gmul(in_b, in_a)")
            break
        print('i={0}'.format(i))
        print('- Input {}:  [{}]'.format(i, inputs.hex()))
        print('- output {}: [{}]'.format(i, output.hex()))
        print('- a: {}, b: {}'.format(hex(in_a), hex(in_b)))
        print('- shares_a: [{}], shares_b: [{}]'.format(shares_a.hex(), shares_b.hex()))
        print('- ab: {}, shares_ab:[{}]'.format(hex(ab), shares_ab.hex()))
        # print('- gfm: {}'.format(hex(gmul)))
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

    # The number of runnung the program
    num = 100000
    uart(serial_port, num)
