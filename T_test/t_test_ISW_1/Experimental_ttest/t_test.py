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

    #####################################################
    def TVLA(self, fix_set, rnd_set):

        # Output of ttest_ind = [t_value, p_value], just first element is needed, [0]
        t_test = ttest_ind(rnd_set, fix_set, axis=0, equal_var=False)[0]

        return t_test

    def Leakage_points(self, t_values):
        leakage_point = []
        for i in range(len(t_values)):
            if abs(t_values[i]) > 4.5:
                leakage_point.append(i)
        return np.array(leakage_point, np.int32)


if __name__ == "__main__":
    name = "t_0_0"
    T_test = T_TEST(name + ".trs")

    all_traces = T_test.traces()
    [r, f, n_r, n_f] = T_test.extract_trace_sets()

    t = T_test.TVLA(r, f)

    leakage_p = T_test.Leakage_points(t)

    print("[+] The percentage of leaky points: {}%".format(len(leakage_p)/T_test.n_s * 100))

    # Plotting T_test result
    #####################################################
    plt.plot(t)

    plt.axhline(y=4.5,  color='r', linestyle='dashed', linewidth=1)
    plt.axhline(y=-4.5, color='r', linestyle='dashed', linewidth=1)

    plt.title("T-test result")
    plt.xlabel("Time point")
    plt.ylabel("t-value")
    plt.grid()
    plt.show()
    # plt.savefig("T_test result_" + name + ".png")
print("Duration of acquisition (sec):", (time.time() - start_time))
print("Duration of acquisition (min):", (time.time() - start_time)/60)
