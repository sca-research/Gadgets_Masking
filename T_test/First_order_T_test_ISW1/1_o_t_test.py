from TRS import TRS
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.stats import ttest_ind

Mask_ORD = 1
step = 10
start_time = time.time()


class T_TEST:
    def __init__(self, filename):
        self.filename = filename
        self.trs = TRS(self.filename)
        self.n_t = self.trs.number_of_traces
        self.n_s = self.trs.number_of_samples
        self.len_p = self.trs.cryptolen

    # Extracting traces from TRS file
    ##################################################################
    def traces(self):
        """ This function extracts all traces from TRS file"""
        all_trace = np.zeros((self.n_t, self.n_s), np.int16)  # Array of samples of each trace
        for i in range(self.n_t):
            all_trace[i] = self.trs.get_trace_sample(i)
        return all_trace

    def extract_trace_sets(self):
        # Regarding to acquisition.py code, the trs file contains both data sets (random and fixed)
        # the first byte of in_data in trs file indicates that the trace belongs to
        # which data set (random_set or fixed_set).
        # The trace belongs to rnd_data_set if random bit(data_set) == 0, and fix_data_set if random bit == 1.
        # Now, regarding the first byte (data_set byte), the two sets are extracted

        all_traces_ = self.traces()

        rnd_trace = []  # rnd_data_set
        fix_trace = []  # fix_data_set

        n_rnd_data_set = 0  # The number of traces in random input set : random inputs
        n_fix_data_set = 0  # The number of traces in  fixed input set : fixed inputs

        for i in range(0, self.n_t):

            # Extracting the data_set byte, which is the first byte of in_data in trs file
            #################################################
            [in_data_int, out_data_int] = self.trs.get_trace_data(i)
            data_set = in_data_int[0]

            if data_set == 0:
                rnd_trace.append(all_traces_[i])
                n_rnd_data_set += 1

            if data_set == 1:
                fix_trace.append(all_traces_[i])
                n_fix_data_set += 1

            n_rnd_fix_traces = n_rnd_data_set + n_fix_data_set

            if n_rnd_fix_traces == self.n_t:
                print("[+] Finishing extracting data_sets")
                break

        fix_trace = np.array(fix_trace, np.int16)
        rnd_trace = np.array(rnd_trace, np.int16)
        print('-------> The trs file contains {} traces'.format(self.n_t))
        print('[+] Each trace contains {:d} samples'.format(self.n_s))
        print('[+] The number of fixed  traces: {}'.format(n_fix_data_set))
        print('[+] The number of random traces: {}'.format(n_rnd_data_set))

        return [fix_trace, rnd_trace, n_fix_data_set, n_rnd_data_set]

    # TVLA test: (DATA‐SET2 = Fix_set and DATA‐SET1 = Rnd_set)
    # a.Group1: First n/2 traces in DATA‐SET 2, First n/2 traces in DATA‐SET 1
    # b.Group2: Last n/2 traces in DATASET 2, n/2 through n traces in DATA‐SET 1
    # c.SubsetA: traces from DATA‐SET2   # Fix_set
    # d.SubsetB: traces from DATA‐SET1   # Rnd_set
    #####################################################
    def TVLA(self, fix_set, rnd_set):

        fix_half = int(len(fix_set) / 2)
        rnd_half = int(len(rnd_set) / 2)

        # t_test between First N/2 traces in rnd_data_set and First N/2 traces in fix_data_set
        # Output of ttest_ind = [t_value, p_value], just first element is needed, [0]
        t_test_1 = ttest_ind(rnd_set[: fix_half], fix_set[: rnd_half], axis=0, equal_var=False)[0]

        # t_test between First N/2 traces in rnd_data_set and First N/2 traces in fix_data_set
        # Output of ttest_ind = [t_value, p_value], just first element is needed, [0]
        t_test_2 = ttest_ind(rnd_set[fix_half:], fix_set[rnd_half:], axis=0, equal_var=False)[0]
        return [t_test_1, t_test_2]

    def Leakage_points(self, t_values):
        leakage_point = []
        for i in range(len(t_values[0])):
            if (abs(t_values[0][i]) > 4.5) and (abs(t_values[1][i]) > 4.5):
                leakage_point.append(i)
        return np.array(leakage_point, np.int32)


if __name__ == "__main__":
    name = "t_8_124"
    T_test = T_TEST(name + ".trs")

    all_traces = T_test.traces()
    [r, f, n_r, n_f] = T_test.extract_trace_sets()

    t = T_test.TVLA(r, f)

    leakage_p = T_test.Leakage_points(t)

    print("[+] The percentage of leaky points: {}%".format(len(leakage_p)/T_test.n_s * 100))

    # Plotting TVLA result
    #####################################################
    plt.plot(t[0], label='Fixed data')
    plt.plot(t[1], label='Random data')

    plt.axhline(y=4.5,  color='r', linestyle='dashed', linewidth=1)
    plt.axhline(y=-4.5, color='r', linestyle='dashed', linewidth=1)

    plt.title("TVLA result")
    plt.xlabel("Time point")
    plt.ylabel("t-value")
    plt.grid()
    plt.legend()
    plt.show()
    plt.savefig("TVLA" + name + ".png")
print("Duration of acquisition (sec):", (time.time() - start_time))
print("Duration of acquisition (min):", (time.time() - start_time)/60)
