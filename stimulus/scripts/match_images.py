# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>
#  Just a little script which was converted from similarly named ipython notebook to 
#  identify offsets and verify identical timing to original manually generated splits
#  of the movie stimuli.
# <codecell>

import random
from os.path import join as pathjoin, basename
import sys
from scipy.misc import imread
from glob import glob
import pylab as pl
import numpy as np
from mvpa2.base import verbose
verbose.level = 2

# <codecell>

#
#targets_dir = '/home/yoh/doc/papers.withothers/raiders_data/data/stimulus/task002/generate/INDIANA_JONES_RAIDERS_LOST_ARK-240x135_10ips'
#matches_dir = '/home/yoh/doc/papers.withothers/raiders_data/data/stimulus/task002/orig/INDIANA_JONES_RAIDERS_LOST_ARK_part_2-240x135_10ips'

targets_dir = sys.argv[1]
matches_dir = sys.argv[2]

FPS = 10 # so we compute timings

target_files = sorted(glob(pathjoin(targets_dir, '*.jpeg')))
match_files = sorted(glob(pathjoin(matches_dir, '*.jpeg')))

# Let's trim match_files a bit for the sake of performance
# Select 600 samples, 200 from each size and then randomly in the middle
match_files_select = range(0, min(200, len(match_files))) \
                     + range(max(len(match_files)-200, 0), len(match_files)) \
                     + [random.randint(0, len(match_files)-1) for i in xrange(200)]
match_files = [f for i, f in enumerate(match_files) if i in set(match_files_select)]
                
def get_idx(fname):
    return int(basename(fname).replace('.jpeg',''))
assert(get_idx('/123/0012.jpeg') == 12)
assert(get_idx('/123/0000.jpeg') == 0)

target_times = np.array(map(get_idx, target_files)).astype(float)/FPS
match_times = np.array(map(get_idx, match_files)).astype(float)/FPS

verbose(1, "There are %d target files for %d files to match" % (len(target_files), len(match_files)))

# <codecell>

def imread_(f):
    verbose(3, f)
    return imread(f).mean(axis=2)[::2,::2]

verbose(1, "Loading %d targets" % len(target_files))
targets = [imread_(f) for f in target_files]

# <codecell>

def get_standardized(imgs):
    arr = np.array([a.flatten() for a in imgs], dtype=np.float32)
    arr -= arr.mean(axis=1)[:, None]
    arr /= arr.std(axis=1)[:, None]
    return arr

def imgs_corr(targets, matches):
    targets_arr = get_standardized(targets)
    matches_arr = get_standardized(matches)
    # we need to standardize each one of them
    out = np.dot(targets_arr, matches_arr.T)/targets_arr.shape[1]
    out[~np.isfinite(out)] = 0
    return out

def silly_imgs_corr(targets, matches):
    # for some basic testing
    manual_corrcoef = np.corrcoef(np.asanyarray([t.flatten() for t in targets]),
                                  np.asanyarray([t.flatten() for t in matches]))
    #print len(targets), len(matches), manual_corrcoef.shape
    out = manual_corrcoef[:len(targets), len(targets):]
    out[~np.isfinite(out)] = 0
    return out

class Corr_to_targets(object):
    def __init__(self, targets):
        self.targets_arr = get_standardized(targets)
    def __call__(self, match):
        match_arr = get_standardized([match])
        out = np.dot(self.targets_arr, match_arr.T)/self.targets_arr.shape[1]
        #import pdb; pdb.set_trace()
        out[~np.isfinite(out)] = 0
        assert(out.shape == (len(self.targets_arr), 1))
        return out[:, 0]

verbose(2, "Running some silly tests")
test_matches = [imread_(f) for f in target_files[:100:10]]
test_pair = targets[50:100:10], test_matches
#pl.figure() ; pl.matshow(silly_imgs_corr(*test_pair)) ; pl.show()
#pl.figure() ; pl.matshow(imgs_corr(*test_pair)) ;
from numpy.testing import assert_array_almost_equal
diff = silly_imgs_corr(*test_pair) - imgs_corr(*test_pair)
assert(np.max(np.abs(diff)) < 0.01)
# pl.matshow(silly_imgs_corr(*test_pair) - imgs_corr(*test_pair)); pl.colorbar();

correr = Corr_to_targets(test_pair[0])
correr_res = np.asanyarray([correr(m) for m in test_pair[1]]).T
assert(np.max(np.abs(imgs_corr(*test_pair) - correr_res)) < 0.01)

# <codecell>

correr = Corr_to_targets(targets)
corrs_to_matches = np.asanyarray([correr(imread_(f)) for f in match_files]).T

# <codecell>

#from mvpa2.base.hdf5 import h5load
#corrs_to_matches = h5load('corrs_to_matches_test.h5')

# <codecell>

# figure out maximal correlations for each "match" to targets
max_matches = np.argmax(corrs_to_matches, axis=0)
assert(len(match_times) == len(max_matches))
matched_times = target_times[max_matches]

# <codecell>

# we need to fit a line, remove all the outliers, compute offset/slope to get reliable coeff for when things started and where ended

import numpy as np
non_outliers = np.ones(len(match_times), dtype=bool)

fits = []
# do few rounds shrinking around the target line
for thr in [100, 10, 1, 0.5, 0.3, 0.1, 0.01, 0.001]:

    if np.sum(non_outliers) < 10:
        verbose(3, "Interrupting since threshold is too tight now")
        break
    scale, offset = np.polyfit(match_times[non_outliers], matched_times[non_outliers], deg=1)
    fit = offset + scale*match_times
    fits.append((fit, scale, offset))
    non_outliers = np.abs(fit - matched_times) <= thr
    verbose(2, "Threshold: %f scale=%.5f (diff=%.5g) offset=%.2f" % (thr, scale, np.abs(scale - 1.0), offset))
    if np.abs(scale - 1.0) < 0.000001:
        # must be enough!
        break

rstrip0 = lambda x:("%.5f" % x).rstrip("0").rstrip(".")

#verbose(2, "Final: start=%.2f stop=%.2f" % (offset, offset + len(match_times)*FPS))
print ("--start-at duration:%s --stop-at duration:%s" % (rstrip0(offset), rstrip0(offset + max(match_times))))
assert(np.abs(scale - 1.0) < 0.000001) # so we have the same FPS

# <codecell>

if False:
    pl.figure(figsize=(16, 4))
    pl.plot(match_times, matched_times)
    for i, (fit, scale, offset) in enumerate(fits):
        pl.plot(match_times, fit, label="fit #%i: %.3g+%3g*i" % (i, offset, scale))
    pl.legend()

# <codecell>


