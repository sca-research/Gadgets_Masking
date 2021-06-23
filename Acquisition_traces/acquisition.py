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


class Acquisition_Gadget(object):
    if __name__ == "__main__":
        # Serial port communication: look this up in 'device manager'
        port = '/dev/ttyUSB0'  # Serial port

        step = 100

        # The length of the TX data in Byte (B)
        # For each gadget, just change Mask_ORD and rnd_gadget
        ##################################################
        Mask_ORD = 1
        main_inputs = 2  # input_a: 1B, input_b: 1B
        rnd_masking_inputs = 2 * Mask_ORD  # Mask_ORD B randomness for masking a, Mask_ORD B randomness for masking b
        rnd_gadget = int(Mask_ORD * (Mask_ORD + 1) / 2)   # ISW_1 multiplication
        input_len = main_inputs + rnd_masking_inputs + rnd_gadget

        # The length of the RX data in Byte (B)
        ##################################################
        output_len = main_inputs + 2 * (Mask_ORD + 1) + (Mask_ORD + 1) + 1  # byte length of output_c: Mask_ORD + 1 (c = a * b)
        print("Output length: ", output_len)
        print("Input length:  ", input_len)


        # Number of traces
        N = 1000
        # Number of samples
        samples = 10000

        # timebase = (2 ^ 1)/10e-9 = 2ns, sampling rate = 500 MSa/s(Page 22, 3.6 Timebase, Programming with the PicoScope 5000 Series (A API))
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

            # A USB 3.0 device is connected to a non-USB 3.0 port.
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
        status["setChA"] = ps.ps5000aSetChannel(chandle, chA, 1, coupling_type, chA_Range, 0)
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

        # Write TRS file header
        #################################################
        # write_header(self, n, number_of_samples, isint, cryptolen, xscale, yscale):
        data_length = input_len + output_len
        trs = TRS_TraceSet.TRS_TraceSet("gadget000.trs")
        # timebase = 1: 2/1e9 = 2 ns = 2e-9
        trs.write_header(N, samples, True, data_length, 2E-9, 1 / 65536)

        # input data
        #################################################
        for i in range(0, N):
            # Generate inputs
            inputs = bytearray([secrets.randbits(8) for j in range(0, input_len)])

            # Run block capture
            #################################################
            # ps5000aRunBlock(handle, noOfPreTriggerSamples, noOfPostTriggerSamples,
            # timebase,* timeIndisposedMs, segmentIndex, lpReady, * pParameter)
            # handle = chandle = ctypes.c_int16()
            status["runBlock"] = ps.ps5000aRunBlock(chandle, pre_Trig_S, post_Trig_S, timebase, None, 0, None, None)
            assert_pico_ok(status["runBlock"])

            # Send inputs through serial port
            #################################################
            ser.write(inputs)

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

            if overflow.value != 0:
                print("overflow!")

            # Write trace into trs file
            #################################################
            trs.write_trace(inputs, output, np.array(Databuffer), True)

            # Checking the correctness of the gadget and printing on the screen
            #################################################
            in_a = output[0]
            in_b = output[1]
            shares_a = output[2:Mask_ORD + 3]
            shares_b = output[Mask_ORD + 3: 2*Mask_ORD + 4]
            shares_ab = output[2 * Mask_ORD + 4: 3*Mask_ORD + 5]
            gmul = output[3*Mask_ORD + 5]

            a = 0
            b = 0
            ab = 0
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
            if i % step == 0:
                print('i={0}'.format(i))
                print('- Input {}:  [{}]'.format(i, inputs.hex()))
                print('- output {}: [{}]'.format(i, output.hex()))
                print('- a: {}, b: {}'.format(hex(in_a), hex(in_b)))
                print('- shares_a: [{}], shares_b: [{}]'.format(shares_a.hex(), shares_b.hex()))
                print('- ab: {}, shares_ab:[{}]'.format(hex(ab), shares_ab.hex()))
                # print('- gfm: {}'.format(hex(gmul)))
                print('___________________________________________________________________')
        trs.close()
    print("The number of traces:", i)
print("Duration of acquistion (sec):",(time.time() - start_time))
