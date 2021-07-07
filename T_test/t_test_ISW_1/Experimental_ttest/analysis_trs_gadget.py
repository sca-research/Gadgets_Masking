from TRS import TRS
import matplotlib.pyplot as plt

Mask_ORD = 1
step = 10


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


name = "t_8_124"
trs = TRS(name+".trs")  # The name of the trs file (name.trs)
print('-------> The trs file contains {} traces'.format(trs.number_of_traces))
print('[+] Each trace contains {:d} samples'.format(trs.number_of_samples))

trs.plot_initial()

for i in range(trs.number_of_traces):

    # Checking the correctness of the gadget and printing on the screen
    #################################################
    [in_data_int, out_data_int] = trs.get_trace_data(i)
    in_data_byte = bytearray([j for j in in_data_int])
    out_data_byte = bytearray([j for j in out_data_int])

    in_a = in_data_byte[1]
    in_b = in_data_byte[2]
    shares_a = in_data_byte[3:Mask_ORD + 4]
    shares_b = in_data_byte[Mask_ORD + 4: 2 * Mask_ORD + 5]
    shares_c = out_data_byte[0:Mask_ORD + 1]

    a = 0
    b = 0
    ab = 0
    for p in range(0, Mask_ORD + 1):
        ab ^= shares_c[p]
        a ^= shares_a[p]
        b ^= shares_b[p]

    if a != in_a:
        print("ERROR: XOR(shares_a)!=in_a")
        break
    if b != in_b:
        print("ERROR: XOR(shares_b)!= in_b")
        break

    gmul = gf_mult(in_a, in_b)

    if gf_mult(in_a, in_b) != ab:
        print("ERROR: XOR(shares_c)!= gmul(in_b, in_a)")
        break
    # if i % step == 0:

    # print('  - minimum value in trace: {0:f}'.format(min(trs.traces[i])))
    # print('  - maximum value in trace: {0:f}'.format(max(trs.traces[i])))
    # print('- in_data {}: {}'.format(i, in_data_byte.hex()))
    # print('- share_c {}: {}'.format(i, out_data_byte.hex()))
    # print('i={0}'.format(i))
    # print('- a: {}, b: {}'.format(hex(in_a), hex(in_b)))
    # print('- shares_a: [{}], shares_b: [{}]'.format(shares_a.hex(), shares_b.hex()))
    # print('- c: {}, shares_c:[{}]'.format(hex(ab), shares_c.hex()))
    # print('- gfmult: {}'.format(hex(gmul)))
    # print('_________________________________________________________________________________________')
    trs.plot_trace(i)
trs.plot_show('Time points', 'V', 'Traces', 'Traces')
# plt.savefig(name + ".png")
