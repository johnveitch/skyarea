#!/usr/bin/env python

import bz2
import glob
import numpy as np
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as pp
from optparse import OptionParser
import plotutils.plotutils as pu
import scipy.stats as ss
import os

USAGE='''%prog [options] ev1_areas.dat ev2_areas.dat ... evN_areas.dat
         Create searched area, sky confidence level, and PP plot using information stored in N areas.dat files, output from run_sky_area.py. If those files are not given, will look in current_dir/I/areas.dat with I in {1..N}'''

parser = OptionParser(USAGE)

parser.add_option('--prefix', default='', help='output file prefix')
parser.add_option('--noinj', action='store_true', default=False, help='disable injection-dependent processing')

options, args = parser.parse_args()
cls = np.array([0.5, 0.75, 0.9])
cls_header = ['area({0:d})'.format(int(round(100.0*cl))) for cl in cls]

data = []
dtype = np.dtype([('simulation_id', np.str, 250),
                  ('p_value', np.float),
                  ('searched_area', np.float),
                  ('area50', np.float),
                  ('area75', np.float),
                  ('area90', np.float)])
if args==None or len(args)==0:
  for file in glob.glob('*/areas.dat'):
    data.append(np.loadtxt(file, dtype=dtype, skiprows=1))
else:
  for file in args:
    data.append(np.loadtxt(file, dtype=dtype, skiprows=1))

new_data = np.zeros(len(data), dtype=data[0].dtype)
for i in range(len(data)):
    new_data[i] = data[i][()]
data = new_data

options.prefix=os.path.realpath(options.prefix)

if not os.path.isdir(options.prefix):
  os.makedirs(options.prefix)

with bz2.BZ2File(os.path.join(options.prefix, 'areas.dat.bz2'), 'w') as out:
    out.write('simulation_id\tp_value\tsearched_area\t' + '\t'.join(cls_header) + '\n')
    for d in data:
        out.write('{0:s}\t{1:g}\t{2:g}\t{3:g}\t{4:g}\t{5:g}\n'.format(d['simulation_id'],
                                                                      d['p_value'],
                                                                      d['searched_area'],
                                                                      d['area50'],
                                                                      d['area75'],
                                                                      d['area90']))
if not options.noinj:
    ks_stat, ks_p = ss.kstest(data['p_value'], lambda x: x)

    pp.clf()
    pu.plot_cumulative_distribution(data['p_value'], '-k')
    pp.plot(np.linspace(0,1,10), np.linspace(0,1,10), '--k')
    pp.xlabel(r'$p_\mathrm{inj}$')
    pp.ylabel(r'$P(p_\mathrm{inj})$')
    pp.title('K-S p-value {0:g}'.format(ks_p))
    pp.savefig(os.path.join(options.prefix, 'p-p.pdf'))
    pp.savefig(os.path.join(options.prefix, 'p-p.png'))

    pp.clf()
    pu.plot_cumulative_distribution(data['searched_area'], '-k')
    pp.xscale('log')
    pp.xlabel(r'Searched Area (deg$^2$)')
    pp.savefig(os.path.join(options.prefix, 'searched-area.pdf'))
pp.clf()
pu.plot_cumulative_distribution(data['area50'], label=str('50\%'))
pu.plot_cumulative_distribution(data['area75'], label=str('75\%'))
pu.plot_cumulative_distribution(data['area90'], label=str('90\%'))    
pp.xscale('log')
pp.xlabel(r'Credible Area (deg$^2$)')
pp.legend(loc='upper left')
pp.savefig(os.path.join(options.prefix, 'credible-area.pdf'))
