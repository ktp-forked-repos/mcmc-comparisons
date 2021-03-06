#!/usr/bin/env python3
#
# plot_comparison.py
#
# BSD 2-Clause License
#
# Copyright (c) 2018, Franco Masotti
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.axes as axes
import numpy as np
import csv
import sys

class Utils():

    def __init__(self, files):
        """ Load the file contents in a dictionary for future easy access."""
        assert isinstance(files, list)
        for f in files:
            assert isinstance(f, dict)
            assert 'name' in f
            assert 'delimiter' in f
            assert 'fields' in f
            assert isinstance(f['name'], str)
            assert isinstance(f['delimiter'], str)
            assert isinstance(f['fields'], list)
            for i in f['fields']:
                assert isinstance(i, str)

        self.data = dict()

        for f in files:
            for i in f['fields']:
                self.data[i] = list()

        for file in files:
            with open(file['name'], 'r') as f:
                data = csv.reader(f, delimiter=file['delimiter'])
                # Sort lines by run number and and keep sample id in place so
                # that we maintain the correct input for the other functions.
                data = sorted(data, key=lambda d: d[0])
                for row in data:
                    self.data[file['fields'][0]].append(int(row[0]))
                    self.data[file['fields'][1]].append(int(row[1]))
                    self.data[file['fields'][2]].append(int(round(float(row[2]))))
                    self.data[file['fields'][3]].append(float(row[3]))
                    self.data[file['fields'][4]].append(int(round(float(row[4]))))
                    self.data[file['fields'][5]].append(float(row[5]))

    def plot_data_sets(self, x_id, y_ids, y_stddev_ids, legend=['set a', 'set b'],
                       title='Comparison', x_label='x', y_label='y', plot_file='plot.png'):
        """ Plot n sets of values for direct comparison."""
        assert isinstance(x_id, str)
        assert isinstance(y_ids, list)
        for e in y_ids:
            assert isinstance(e, str)
        assert isinstance(y_stddev_ids, list)
        for e in y_stddev_ids:
            assert isinstance(e, str)
        assert isinstance(legend, list)
        for e in legend:
            assert isinstance(e, str)
        assert (len(y_ids) == len(y_stddev_ids) == len(legend))

        for i in range(0,len(y_ids)):
            plt.errorbar(self.data[x_id],self.data[y_ids[i]],yerr=self.data[y_stddev_ids[i]],markersize=2.5,linestyle='-',marker='o', capsize=2.5)
        plt.title(title)
        plt.legend(legend)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.savefig(plot_file)
        # Flush output. Without this consecutive plots overlap.
        # See: https://stackoverflow.com/questions/17106288/matplotlib-pyplot-will-not-forget-previous-plots-how-can-i-flush-refresh
        plt.gcf().clear()

    # Rows name and cols name must be the same for all cases.
    def compute_avg_and_stddev_data_sets(self, dim_id, rows_name, cols_name):
        assert isinstance(dim_id, list)
        for e in dim_id:
            assert isinstance(e, str)
        assert isinstance(rows_name, str)
        assert isinstance(cols_name, str)

        # Init.
        rows = max(self.data[rows_name])
        cols = len(set(self.data[cols_name]))
        dim=dict()
        for k in dim_id:
            dim[k]=list()
            dim['stddev_' + k]=list()

        # Transform the original data into a matrix of size rows x cols, where:
        #   rows = current run
        #   columns = current sample set
        # matrix_dim is a set of matrices.
        matrix_dim=dict()
        for k in dim_id:
            matrix_dim[k]=np.matrix(self.data[k])
            matrix_dim[k]=matrix_dim[k].reshape(rows, cols)

        #   matrix_dim[i]:
        #
        #    Samples    1000    2000    3000    ...
        # Run           ---------------------------
        #           1  | times or probs
        #           2  |
        #           3  |
        #           .. |
        #               sum_0   sum_1   sum_i
        #
        #        avg_i = sum_i / #(runs)

        # Compute average and standard deviation
        # of the running times for each sample.
        for c in range(0, cols):
            sum=dict()
            stddev_buf=dict()
            for k in dim_id:
                sum[k] = 0
                stddev_buf[k] = list()
            for r in range(0,rows):
                # To compute the average, we need to sum elements of the same
                # column so we need to iterate by row.
                for k in dim_id:
                    sum[k] += matrix_dim[k].item(r,c)
                    stddev_buf[k].append(matrix_dim[k].item(r,c))
            for k in dim_id:
                # Compute avgs by column.
                dim[k].append(sum[k]/rows)
                dim['stddev_' + k].append(np.std(stddev_buf[k]))

        return dim

    def plot_frontend(self, plot_title, plot_file, running_times, running_times_stddev, legend, y_label):
            assert isinstance(plot_title,str)
            assert isinstance(plot_file,str)
            assert isinstance(running_times, list)
            for e in running_times:
                assert isinstance(e, str)
            assert isinstance(running_times_stddev, list)
            for e in running_times_stddev:
                assert isinstance(e, str)
            assert isinstance(legend, list)
            for e in legend:
                assert isinstance(e, str)
            assert isinstance(y_label, str)

            self.plot_data_sets('samples',
                            running_times,
                            running_times_stddev,
                            legend,
                            plot_title,
                            'samples',
                            y_label,
                            plot_file)

    def overwrite_data_set_with_avg(self, dims_avg):
        assert isinstance(dims_avg, dict)

        for key, value in dims_avg.items():
            if key == 'run_number' or key == 'samples':
                # Remove duplicates from these two sets.
                self.data[key]=sorted(list(set(self.data[key])))
            else:
                self.data[key]=value


class MhVsGibbs(Utils):
    def __init__(self, filename, delimiter=','):
        file={ 'name': filename, 'delimiter': delimiter, 'fields': ['run_number', 'samples', 'mh_time', 'mh_prob', 'gibbs_time', 'gibbs_prob'] }
        files=[file]
        super().__init__(files)

    def plot_mh_vs_gibbs_times(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['mh_time','gibbs_time'], ['stddev_mh_time','stddev_gibbs_time'], ['mh', 'gibbs'], 'running time (ms)')

    def plot_mh_vs_gibbs_probs(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['mh_prob','gibbs_prob'], ['stddev_mh_prob','stddev_gibbs_prob'], ['mh', 'gibbs'], 'probability [0,1]')

    def mh_vs_gibbs_avg(self):
        avgs = self.compute_avg_and_stddev_data_sets(['mh_time',
            'gibbs_time', 'mh_prob', 'gibbs_prob'],
            'run_number','samples')
        avgs['run_number']=self.data['run_number']
        avgs['samples']=self.data['samples']
        self.overwrite_data_set_with_avg(avgs)


class ArithmSampleMhVsGibbs(MhVsGibbs):
    def arithm_sample_mh_vs_gibbs_avg(self):
        self.mh_vs_gibbs_avg()
        self.plot_mh_vs_gibbs_times('arithm_sample mh vs gibbs times avg',
                              'plot_arithm_sample_mh_vs_gibbs_times.png')
        self.plot_mh_vs_gibbs_probs('arithm_sample mh vs gibbs probs avg',
                              'plot_arithm_sample_mh_vs_gibbs_probs.png')


class Test33SampleMhVsGibbs(MhVsGibbs):
    def test33_sample_mh_vs_gibbs_avg(self):
        self.mh_vs_gibbs_avg()
        self.plot_mh_vs_gibbs_times('test33_sample mh vs gibbs times avg',
                              'plot_test33_sample_mh_vs_gibbs_times.png')
        self.plot_mh_vs_gibbs_probs('test33_sample mh vs gibbs probs avg',
                              'plot_test33_sample_mh_vs_gibbs_probs.png')


class Test66SampleMhVsGibbs(MhVsGibbs):
    def test66_sample_mh_vs_gibbs_avg(self):
        self.mh_vs_gibbs_avg()
        self.plot_mh_vs_gibbs_times('test66_sample mh vs gibbs times avg',
                              'plot_test66_sample_mh_vs_gibbs_times.png')
        self.plot_mh_vs_gibbs_probs('test66_sample mh vs gibbs probs avg',
                              'plot_test66_sample_mh_vs_gibbs_probs.png')


class Amcmc(Utils):
    def __init__(self, filename, delimiter=','):
        file={ 'name': filename, 'delimiter': delimiter, 'fields': ['run_number', 'samples', 'adapt_on_time', 'adapt_on_prob', 'adapt_off_time', 'adapt_off_prob'] }
        files=[file]
        super().__init__(files)

    def plot_adapt_on_vs_adapt_off_times(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['adapt_on_time','adapt_off_time'], ['stddev_adapt_on_time','stddev_adapt_off_time'], ['adapt_on', 'adapt_off'], 'running time (ms)')

    def plot_adapt_on_vs_adapt_off_probs(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['adapt_on_prob','adapt_off_prob'], ['stddev_adapt_on_prob','stddev_adapt_off_prob'], ['adapt_on', 'adapt_off'], 'probability [0,1]')

    def adapt_on_vs_adapt_off_avg(self):
        avgs = self.compute_avg_and_stddev_data_sets(['adapt_on_time',
            'adapt_off_time', 'adapt_on_prob', 'adapt_off_prob'],
            'run_number','samples')
        avgs['run_number']=self.data['run_number']
        avgs['samples']=self.data['samples']
        self.overwrite_data_set_with_avg(avgs)


class Test33CondProbAdaptOnVsAdaptOff(Amcmc):
    def test33_cond_prob_adapt_on_vs_adapt_off_avg(self):
        self.adapt_on_vs_adapt_off_avg()
        self.plot_adapt_on_vs_adapt_off_times('test33_cond_prob adapt_on vs adapt_off times avg',
                              'plot_test33_cond_prob_adapt_on_vs_adapt_off_times.png')
        self.plot_adapt_on_vs_adapt_off_probs('test33_cond_prob adapt_on vs adapt_off probs avg',
                              'plot_test33_cond_prob_adapt_on_vs_adapt_off_probs.png')


class Test66CondProbAdaptOnVsAdaptOff(Amcmc):
    def test66_cond_prob_adapt_on_vs_adapt_off_avg(self):
        self.adapt_on_vs_adapt_off_avg()
        self.plot_adapt_on_vs_adapt_off_times('test66_cond_prob adapt_on vs adapt_off times avg',
                              'plot_test66_cond_prob_adapt_on_vs_adapt_off_times.png')
        self.plot_adapt_on_vs_adapt_off_probs('test66_cond_prob adapt_on vs adapt_off probs avg',
                              'plot_test66_cond_prob_adapt_on_vs_adapt_off_probs.png')


class FourWayComparison(Utils):
    def __init__(self, file_names, delimiter=','):
        assert isinstance(file_names, dict)
        assert 'amcmc' in file_names
        assert 'no_amcmc' in file_names

        file_a={ 'name': file_names['amcmc'], 'delimiter': delimiter, 'fields': ['run_number', 'samples', 'adapt_on_time', 'adapt_on_prob', 'adapt_off_time', 'adapt_off_prob'] }
        file_b={ 'name': file_names['no_amcmc'], 'delimiter': delimiter, 'fields': ['run_number', 'samples', 'mh_time', 'mh_prob', 'gibbs_time', 'gibbs_prob'] }
        files=[file_a, file_b]
        super().__init__(files)

    def plot_times(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['adapt_on_time','adapt_off_time', 'mh_time', 'gibbs_time'], ['stddev_adapt_on_time','stddev_adapt_off_time', 'stddev_mh_time', 'stddev_gibbs_time'], ['adapt_on', 'adapt_off', 'mh', 'gibbs'], 'running time (ms)')

    def plot_probs(self, plot_title, plot_file):
        self.plot_frontend(plot_title, plot_file, ['adapt_on_prob','adapt_off_prob', 'mh_prob', 'gibbs_prob'], ['stddev_adapt_on_prob','stddev_adapt_off_prob', 'stddev_mh_prob', 'stddev_gibbs_prob'], ['adapt_on', 'adapt_off', 'mh', 'gibbs'], 'probability [0,1]')

    def compute_avg(self):
        avgs = self.compute_avg_and_stddev_data_sets(['mh_time',
            'gibbs_time', 'mh_prob', 'gibbs_prob', 'adapt_on_time',
            'adapt_off_time', 'adapt_on_prob', 'adapt_off_prob'],
            'run_number','samples')
        avgs['run_number']=self.data['run_number']
        avgs['samples']=self.data['samples']
        self.overwrite_data_set_with_avg(avgs)


class Test33FourWayComparison(FourWayComparison):
    def test33_four_way_comparison_avg(self):
        self.compute_avg()
        self.plot_times('test33 times avg',
                        'plot_test33_times.png')
        self.plot_probs('test33 probs avg',
                        'plot_test33_probs.png')


def main():
    # This is necessary to save the plot to a file instead of displaying it directly.
    matplotlib.use('Agg')
    # Get the file names from argv. This decides the type of plot.
    file_name_a=sys.argv[1]
    if len(sys.argv) == 3:
        # Plot two tests.
        file_name_b=sys.argv[2]
    else:
        # Plot a single test.
        file_name_b=''
    delimiter=','
    if file_name_a == 'test33_sample.csv' and file_name_b == 'test33_cond_prob.csv':
        speeds = Test33FourWayComparison({ 'no_amcmc': file_name_a , 'amcmc': file_name_b }, delimiter)
        speeds.test33_four_way_comparison_avg()
    elif file_name_a == 'arithm_sample.csv':
        speeds = ArithmSampleMhVsGibbs(file_name_a,delimiter)
        speeds.arithm_sample_mh_vs_gibbs_avg()
    elif file_name_a == 'test33_sample.csv':
        speeds = Test33SampleMhVsGibbs(file_name_a,delimiter)
        speeds.test33_sample_mh_vs_gibbs_avg()
    elif file_name_a == 'test66_sample.csv':
        speeds = Test66SampleMhVsGibbs(file_name_a,delimiter)
        speeds.test66_sample_mh_vs_gibbs_avg()
    elif file_name_a == 'test33_cond_prob.csv':
        speeds = Test33CondProbAdaptOnVsAdaptOff(file_name_a,delimiter)
        speeds.test33_cond_prob_adapt_on_vs_adapt_off_avg()
    elif file_name_a == 'test66_cond_prob.csv':
        speeds = Test66CondProbAdaptOnVsAdaptOff(file_name_a,delimiter)
        speeds.test66_cond_prob_adapt_on_vs_adapt_off_avg()

if __name__ == '__main__':
    main()
