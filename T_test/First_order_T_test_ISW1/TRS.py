# Reading TRS file, Showing Data, Plotting Traces
import trsfile
import numpy as np
import matplotlib.pyplot as plt

Mask_ORD = 1

# length_data (cryptolen in TRS) is:
# in_data = data_set (= rnd_or_fix) + in_a + in_b + input_of_gadget (= mask_a + mask_b + rnd_gadget)
# in_data_len = 1 + 1 + 1 + [(Mask_ORD + 1) + (Mask_ORD + 1) + Mask_ORD * (Mask_ORD + 1)/2]
# output = The shares of the output of the gadget, shares_c ( c = a * b), shares_out
# output_len = (Mask_ORD + 1)
# data_length = in_data + output_len
# data_length = 3 + 2 * (Mask_ORD + 1) + Mask_ORD *(Mask_ORD + 1)/2 + (Mask_ORD + 1)


class TRS:
    def __init__(self, trs_file_name) -> object:
        trace_root = trsfile.open(trs_file_name, 'r')
        self.pos = trace_root.engine.data_offset  # data_offset
        headers = trace_root.engine.headers
        for header, value in headers.items():  # Gives the access to key & value f header
            if 'NUMBER_TRACES' in header.name:
                self.number_of_traces = value
            elif 'NUMBER_SAMPLES' in header.name:
                self.number_of_samples = value
            elif 'SAMPLE_CODING' in header.name:
                self.is_float = value.is_float  # sample_coding
            elif 'LENGTH_DATA' in header.name:
                # data_length = 3 + 2 * (Mask_ORD + 1) + Mask_ORD *(Mask_ORD + 1)/2 + (Mask_ORD + 1)
                self.cryptolen = value
        self.in_data_len = 3 + 2 * (Mask_ORD + 1) + Mask_ORD * (Mask_ORD + 1) / 2
        self.output_len = (Mask_ORD + 1)
        self.data_length = 3 + 2 * (Mask_ORD + 1) + Mask_ORD * (Mask_ORD + 1) / 2 + (
                Mask_ORD + 1)  # in_data_len + output_len
        self.traces = [trace_root[i] for i in range(self.number_of_traces)]

    def get_trace_sample(self, ind):  # ind = index # Gives the samples of the index_th trace
        if ind < self.number_of_traces:
            return self.traces[ind].samples

    def get_trace_data(self, ind):  # Gives the data of the index_th trace
        # input data = set( = rnd_or_fix) + in_a + in_b + input_of_gadget( = mask_a + mask_b + rnd_gadget)
        in_data_ind = np.zeros((int(self.in_data_len)), np.dtype('B'))
        # The shares of the output of the gadget (shares_c) c = a * b
        c_ind = np.zeros((int(self.output_len)), np.dtype('B'))
        d_ind = self.traces[ind].data

        if ind < self.number_of_traces:  # Check the correctness of the number_of_traces
            in_data_length = int(self.in_data_len)
            # Extracting in_data
            for i in range(0, in_data_length):
                in_data_ind[i] = d_ind[i]

            # Extracting output data
            for i in range(in_data_length, int(self.data_length)):
                c_ind[i - in_data_length] = d_ind[i]

        return [in_data_ind, c_ind]

    def x_axis(self, r1, r2):
        return [item for item in range(r1, r2 + 1)]

    def plot_initial(self):
        fig, ax = plt.subplots()
        self.ax = ax
        self.fig = fig

    def plot_trace(self, ind=0):
        y_data = self.get_trace_sample(ind)
        x_data = self.x_axis(1, len(y_data))
        self.ax.plot(x_data, y_data)

    def plot_trace_input(self, trace):
        """ Plotting the trace as an input"""
        self.trace = trace
        self.x_data = self.x_axis(1, len(trace))
        self.ax.plot(self.x_data, trace)

    def phrase_plot(self, phrase):
        self.ax.plot(self.x_data, self.trace, label=hex(phrase))
        self.ax.legend()

    def plot_show(self, x_l, y_l, title_l, name):
        self.ax.set(xlabel=x_l, ylabel=y_l, title=title_l)
        self.ax.grid()
        self.fig.savefig(name + ".png")
        plt.show()
