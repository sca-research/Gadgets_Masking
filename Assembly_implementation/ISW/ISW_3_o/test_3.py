
import serial
import os
from time import sleep



def uart(ser_port, num_repeat):
    """ This function enables the serial_port, and transmits tx_data
        from the PC to the device connected with the PC and receives
        rx_data from the device to the PC. Also it repeats the TX and RX
        transactions num_repeat times"""

    # The length of the TX data in Byte (B)
    input_length = 14  # a: 1B, b: 1B, rnd: 12B (3B for masking a, 3B for masking b, 6B for ISW multiplication)

    # The length of the RX data in Byte (B)
    output_length = 15  # a: 1B, b: 1B, shares_a: 4B, shares_b: 4B, shares_a*b: 4B, output of gmul func in main.c: 1B

    # Enabling the serial port
    serial_p = serial.Serial(ser_port)

    if serial_p.is_open:
        print("\n ********************* START ********************* \n")

    for i in range(num_repeat):

        # Generating random inputs and randomness (a, b, r)
        input_data = os.urandom(input_length)



        # Wait
        # tx: Transmitting input data serially from the PC to the SCALE_Board by UART Serial Port
        sleep(0.1)
        serial_p.write(input_data)

        # rx: Receiving output data serially from the SCALE_Board to the PC  by UART Serial Port
        rx_ = serial_p.read(output_length)

        in_a = rx_[0]
        in_b = rx_[5]
        shares_a = rx_[1:5]
        shares_b = rx_[6:10]
        shares_ab = rx_[10:14]
        gmul = rx_[14]
        ab = shares_ab[0] ^ shares_ab[1] ^ shares_ab[2] ^ shares_ab[3]
        a = shares_a[0] ^ shares_a[1] ^ shares_a[2] ^ shares_a[3]
        b = shares_b[0] ^ shares_b[1] ^ shares_b[2] ^ shares_b[3]

        if gmul != ab:
            print("ERROR: XOR(shares_ab)!= gmul(in_b, in_a)")
            break

        print('\n- out{}:  [{}]'.format(i, rx_.hex()))
        print('\n- a: {}, b: {}'.format(hex(in_a), hex(in_b)))
        print('\n- shares_a: [{}], shares_b: [{}]'.format(shares_a.hex(), shares_b.hex()))
        print('\n- ab: {}, shares_ab:[{}]'.format(hex(ab), shares_ab.hex()))
        print('\n- gfm: {}'.format(hex(gmul)))
        print(hex(shares_ab[0]))
        print(hex(shares_ab[1]))
        print(hex(shares_ab[2]))
        print('\n- a: {}'.format(hex(a)))
        print('\n- b: {}'.format(hex(b)))


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
    num = 100
    uart(serial_port, num)
