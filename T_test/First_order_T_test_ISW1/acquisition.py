import sys
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import mV2adc, assert_pico_ok
import random
import serial
import time
import ctypes
import numpy as np
import TRS_TraceSet
import secrets

start_time = time.time()

Mask_ORD = 1


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


# The variables that are depend on the individual gadget:
# Mask_ORD, n_rnd_gadget, samples, timebase, threshold, xscale
class Acquisition_Gadget(object):
    if __name__ == "__main__":
        # Serial port communication: look this up in 'device manager'
        port = '/dev/ttyUSB0'  # Serial port

        step = 1000  # Printing the related data on screen after 100 acquisition

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

        # Number of traces
        N = 10000
        # Number of samples
        samples = 10000

        # timebase = (2 ^ 1)/10e-9 = 2ns, sampling rate = 500 MSa/s
        # (Page 22, 3.6 Timebase, Programming with the PicoScope 5000 Series (A API))
        timebase = 1

        # Initialized random generator for generating inputs and randomness
        ##################################################
        random.seed()

        # Open serial port
        ##################################################
        ser = serial.Serial(port)
        print("Opening the serial port ...")

        # Wait for 200ms
        time.sleep(0.1)

        # Connect the scope
        # Create chandle and status ready for use
        ##################################################
        chandle = ctypes.c_int16()
        status = {}

        # Open 5000 series PicoScope
        #################################################
        # ps5000aOpenUnit(*handle, *serial, resolution)
        # handle = chandle = ctypes.c_int16()
        # serial = None: the serial number of the scope
        # Resolution set to 8 Bit
        resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_8BIT"]
        # Returns handle to chandle for use in future API functions
        status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(chandle), None, resolution)

        try:
            assert_pico_ok(status["openunit"])
        except:  # PicoNotOkError:

            powerStatus = status["openunit"]

            # When a USB 3.0 device is connected to a non-USB 3.0 port, this means:
            # PICO_USB3_0_DEVICE_NON_USB3_0_PORT = (uint)0x0000011EUL == 286;
            if powerStatus == 286:
                status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
            else:
                raise
            assert_pico_ok(status["changePowerSource"])

        # Set up channel A
        print("Preparing channel A ...")
        #################################################
        # ps5000aSetChannel(handle, channel, enabled, coupling_type, ch_Range, analogueOffset)
        # handle = chandle = ctypes.c_int16()
        chA = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        chA_Range = ps.PS5000A_RANGE["PS5000A_1V"]
        status["setChA"] = ps.ps5000aSetChannel(chandle, chA, 1, coupling_type, chA_Range, 0.1)
        assert_pico_ok(status["setChA"])

        # Set up channel B
        print("Preparing channel B ...")
        #################################################
        # ps5000aSetChannel(handle, channel, enabled, coupling_type, ch_Range, analogueOffset)
        # handle = chandle = ctypes.c_int16()
        chB = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        chB_Range = ps.PS5000A_RANGE["PS5000A_5V"]
        status["setChB"] = ps.ps5000aSetChannel(chandle, chB, 1, coupling_type, chB_Range, 0)
        assert_pico_ok(status["setChB"])

        # Set up signal trigger (Using Channel B)
        print("Preparing the trigger through channel B ...")
        #################################################
        post_trigger = True
        # trigger threshold(mV)
        threshold = 2000
        # trigger direction
        posedge_trigger = True
        delay = 0

        if post_trigger:
            pre_Trig_S = 0  # preTriggerSamples
            post_Trig_S = samples  # postTriggerSamples
        else:
            pre_Trig_S = samples
            post_Trig_S = 0

        # ps5000aSetSimpleTrigger(handle, enable,source, threshold, direction, delay, autoTrigger_ms)
        # handle = chandle = ctypes.c_int16()
        source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        # mV2adc(millivolts, range, maxADC): Takes a voltage value and converts it into adc counts
        # maxADC = ctypes.c_int16(32512) # 32512 the Max value that PicoScope can represent.
        # however it should be 2 ^ 16 = 65536
        # when vertical values are represented by integer,
        # they are always in range (the range of vertical axis) [-32512, 32512]* uint
        # [-5v, 5V]
        threshold = mV2adc(threshold, chB_Range, ctypes.c_int16(32512))
        direction_rising = ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_RISING"]
        direction_falling = ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_FALLING"]

        if posedge_trigger:
            status["trigger"] = ps.ps5000aSetSimpleTrigger(chandle, 1, source, threshold, direction_rising, delay, 0)

        else:
            status["trigger"] = ps.ps5000aSetSimpleTrigger(chandle, 1, source, threshold, direction_falling, delay, 0)

        assert_pico_ok(status["trigger"])

        # Create buffers ready for assigning pointers for data collection
        #################################################
        # ps5000aSetDataBuffers(handle, source, * bufferMax, * bufferMin, bufferLth, segmentIndex, mode)
        # handle = chandle = ctypes.c_int16()
        Databuffer = (ctypes.c_int16 * samples)()
        point_bufferMax = ctypes.byref(Databuffer)
        status["setDataBuffers0"] = ps.ps5000aSetDataBuffers(chandle, 0, point_bufferMax, None, samples, 0, 0)
        assert_pico_ok(status["setDataBuffers0"])

        # Write TRS file header:
        # The data stored in trs file is:
        # 1: data_set(for indicating the data is random or fix) + 2: input_a + 3: input_b +
        # 4: input_of_gadget (= mask_a + mask_b + rnd_gadget) + 5: shares of the output of the gadget
        #################################################
        # write_header(self, n, number_of_samples, isint, cryptolen, xscale, yscale):

        trs = TRS_TraceSet.TRS_TraceSet("t_0_0.trs")
        # 65536 = 2 ^ 16
        # yscale is Vertical UNIT. unit=ChannelA.range/65536.
        # chA_Range = ps.PS5000A_RANGE["PS5000A_1V"]: 1 V ---> 1\65536
        # timebase = 1: 2/1e9 = 2 ns = 2e-9

        # data = data_set (= rnd_or_fix) + in_a + in_b + input_of_gadget (= mask_a + mask_b + rnd_gadget)
        # data = 1 + 1 + 1 + input_len_gadget = 3 + input_len_gadget
        data = 3 + input_len_gadget
        data_length = data + output_len
        print("data", data_length)

        trs.write_header(2 * N, samples, True, data_length, 2E-9, 1 / 65536)

        # input data (fix_VS_random)
        #################################################
        n_rnd_data_set = 0  # The number of traces in random input set : random inputs
        n_fix_data_set = 0  # The number of traces in  fixed input set : fixed inputs

        for i in range(0, 2 * N):

            # Generate inputs of the gadget
            ##################################################
            # Choosing data_set randomly: rnd_data_set if random bit == 0, fix_data_set if random bit == 1,
            fix_or_rnd_data = random.getrandbits(1)  # Pick a random bit

            # input_a and input_b are sampled in "int" type for
            # being convince to use in masking function and gf_mult function

            # if the random bit is == 0, pick rnd_data_set
            if fix_or_rnd_data == 0:
                data_set = (0).to_bytes(1, sys.byteorder)  # 0 means data is belongs to rnd_data_set
                input_a = secrets.randbits(8)  # type: int
                input_b = secrets.randbits(8)  # type: int
                n_rnd_data_set += 1

            # if the random bit is == 1, pick fix_data_set
            else:
                data_set = (1).to_bytes(1, sys.byteorder)  # 1 means data is belongs to fix_data_set
                input_a = 0
                input_b = 0
                n_fix_data_set += 1

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

            # Run block capture
            #################################################
            # ps5000aRunBlock(handle, noOfPreTriggerSamples, noOfPostTriggerSamples,
            # timebase,* timeIndisposedMs, segmentIndex, lpReady, * pParameter)
            # handle = chandle = ctypes.c_int16()
            status["runBlock"] = ps.ps5000aRunBlock(chandle, pre_Trig_S, post_Trig_S, timebase, None, 0, None, None)
            assert_pico_ok(status["runBlock"])

            # Send inputs through serial port
            #################################################
            ser.write(inputs_of_gadget)

            # Receive outputs through serial port
            #################################################
            # Read outputs
            output = bytearray(ser.read(output_len))

            # Check for data collection to finish using ps5000aIsReady
            #################################################
            # ps5000aIsReady(chandle, * ready)
            # handle = chandle = ctypes.c_int16()
            ready = ctypes.c_int16(0)
            check = ctypes.c_int16(0)
            while ready.value == check.value:
                status["isReady"] = ps.ps5000aIsReady(chandle, ctypes.byref(ready))

            # Create overflow location
            #################################################
            # ps5000aGetValues(handle, startIndex, * noOfSamples, downSampleRatio,
            # downSampleRatioMode, segmentIndex, * overflow)
            # handle = chandle = ctypes.c_int16()
            overflow = ctypes.c_int16()
            # create converted type maxSamples
            cTotalSamples = ctypes.c_int32(samples)

            # Retried data from scope to buffers assigned above
            point_samples = ctypes.byref(cTotalSamples)  # pointer to number of samples
            point_overflow = ctypes.byref(overflow)  # pointer to overflow
            status["getValues"] = ps.ps5000aGetValues(chandle, 0, point_samples, 0, 0, 0, point_overflow)
            assert_pico_ok(status["getValues"])

            # If Overflow occurs, change the value analogueOffset in ps5000aSetChannel
            if overflow.value != 0:
                print("overflow!")

            # Write trace into trs file
            #################################################
            # The Data need to be saved in trs file
            data = bytearray(data_set + in_a + in_b + inputs_of_gadget)

            trs.write_trace(data, output, np.array(Databuffer), True)

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
                print('- Input {}:  [{}]'.format(i, data.hex()))
                print('- output {}: [{}]'.format(i, output.hex()))
                print('- a: {} ---> shares_a: [{}]'.format(in_a.hex(), mask_a.hex()))
                print('- b: {} ---> shares_b: [{}]'.format(in_b.hex(), mask_b.hex()))
                print('- c: {} ---> shares_c:[{}]'.format(hex(out_c), output.hex()))
                print('- gfm: {}'.format(hex(gf_mult(input_a, input_b))))
                print('___________________________________________________________________')

            # Check the number of whole traces in both data sets is not grater than 2 * N
            if n_rnd_data_set + n_fix_data_set == 2 * N + 1:
                print("[+] The acquisition is finished")
                break

        # Closing the trs file
        #################################################
        trs.close()
    print("The number of traces:", i + 1)


print("Duration of acquisition (sec):", (time.time() - start_time))
print("Duration of acquisition (min):", (time.time() - start_time) / 60)
