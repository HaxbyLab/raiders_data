Dataset content overview
========================

git-annex 101
-------------

This repository is commonly distributed as a
[git-annex](http://git-annex.branchable.com) repository.  To initially
obtain it, or to fetch additional changes you would need to

    git clone for-now-secret-host:/secret/location.git raiders
    cd raiders

To obtain content for any "large" file or entire directories

    git annex get WHATEVER-FILES-YOU-NEED

To fetch new changes later:

    git pull # or git fetch; git merge origin/master
	git annex get WHATEVER-FILES-YOU-NEED

**Hint**: use `git annex get -J 4` to establish 4 parallel streams to
  fetch the data -- should speed up transfer considerably.

To add new content (possibly in a new branch, see `git branch`):

- add only small files (text, scripts, etc) directly to git with

        git add FILES

- add large files (images, data) to git-annex with

        git annex add FILES

- commit added content into git (large files added to
  annex will not be added directly but placed under .git/annex/objects)


        git commit -m "Description of the changes"

To submit your changes to the original server

- push git repository

        git push

- send the new annex content to the server

        git annex copy --to=origin . # or specific files/directories


Data layout
-----------

Data is organized largely following
[openfmri.org](http://openfmri.org) convention.  Currently it contains
data only for the "task002", as described in `task_key.txt` being
"Raiders movie. Dartmouth sample #1 (8ch coil, 8 runs)".

Top directory contains following sub-directories, many of which
contains other sub-directories groupping data according to the
modality (e.g. BOLD, Blood Oxygen Level Dependent, for functional MRI
data) and task (e.g. task002) or even task and run
(e.g. task002_run001).

Top directories:

- aligned/
  Data aligned across all subjects, e.g. aligned/BOLD/task002 contains
  hyper-aligned BOLD data
- masks/
  Common masks
- scripts/
  Scripts used for various stages in pre-processing or dataset preparation
- stimulus/
  Data (non-redistributable) and scripts/ for stimuli delivery
- sub*/
  Data for each subject


Design
------

There were 8 acquisition runs in task002, for which entire movie was
cut into 8 approximately equal in length, with about 20 seconds of
movie overlap between runs (i.e. last 20 seconds of the movie at the
end of the first run were shown at the beginning of the 2nd run).
Details on length etc could be found in a [google spreadsheet]
(https://docs.google.com/spreadsheets/d/1vs37Tdr_ynA1c9skVvy4JhFJM1SqAYhX6Z1QSDuCUB4/edit?usp=sharing).

Stimuli
-------

In a current (private, non-redistributable) version of the repository
`stimulus/task002/generate/` contains regenerated from a DVD (use
script `stimulus/scripts/dvd-to-mks` to re-generate your own copy)
video fragments, and per-frame images for the first part
(`stimulus/task002/generate/INDIANA_JONES_RAIDERS_LOST_ARK_part_1-182x121/`).
Script `stimulus/scripts/video2jpeg-x121` could be used to generate a
sequence of images at that resolution (182x121).

Functional imaging
------------------


#### Raw BOLD functional MRI


Filename examples for subject 001 and run 001

- `sub001/BOLD/task002_run001/bold.{PAR,REC}`
  Original BOLD data as acquired from the scanner
- `sub001/BOLD/task002_run001/bold.nii.gz`
  Original BOLD data in NIfTI format, as converted from {PAR,REC}
  using dcm2nii tool

#### Pre-processed BOLD functional MRI

Currently we provide a sample of data as it was pre-processed by
Swaroop Guntupalli, hence suffix `_sw1` and used in the
[Hyperalignment paper][HGC+11], e.g.

- `sub001/BOLD/task002_run001/bold_sw1_stc_reg_despike_dt_bp.nii.gz`
  Pre-processed functional data for subject 1, run 1, in original subject
  space (so "voxels" do not "align" across subjects).  Abbreviations used:

     - _stc -- slice timing correction
     - _reg -- registered (motion corrected)
	 - _despite -- de-spiked (high-freq artifacts removed)
     - _bp -- band-pass filtered

  Basic detail on the file:

    > nib-ls sub001/BOLD/task002_run001/bold_sw1_stc_reg_despike_dt_bp.nii.gz 
    ... float32 [ 80,  80,  41, 336] 3.00x3.00x3.00x2.50  #exts: 1

- `sub001/BOLD/task002/bold_sw1_stc_reg_despike_dt_bp_mni.nii.gz`
  Pre-processed data for subject 1, **all runs concatenated**, in MNI
  space, after linear anatomical alignment

        > nib-ls sub001/BOLD/task002/bold_sw1_stc_reg_despike_dt_bp_mni.nii.gz
        ... float32 [ 61,  73,  61, 2718] 3.00x3.00x3.00x2.50  #exts: 1

- `aligned/BOLD/task002/bold_surfslhyper_sw1_radius20_lr32_hr128_full_featsel0.7.hdf5.gz`
  Hyperalignment projections estimated per each subject.  It is an HDF5 dataset, relatively large!, which
  you can load using `mvpa2` functionality in Python:

```python
from mvpa2.base.hdf5 import h5load
bold_surfslhyper = h5load('aligned/BOLD/task002/bold_surfslhyper_sw1_radius20_lr32_hr128_full_featsel0.7.hdf5.gz')
# TODO
```

[HGC+11]: http://www.sciencedirect.com/science/article/pii/S0896627311007811	"Haxby, J. V. , Guntupalli, J. S. , Connolly, A. C. , Halchenko, Y. O. , Conroy, B. R., Gobbini, M. I. , Hanke, M. and Ramadge, P. J. (2011). A Common, High-Dimensional Model of the Representational Space in Human Ventral Temporal Cortex. Neuron, 72, 404-416.  DOI: 10.1016/j.neuron.2011.08.026,"


Recommended analysis environment
--------------------------------

We would recommend to use some Debian/Ubuntu Linux environment
(native, docker (neurodebian), or VM such as
[NeuroDebian VM](http://neuro.debian.net/vm.html)) with
[NeuroDebian](http://neuro.debian.net) repository enabled.

Then you could install a large collection of relevant tools which
would facilitate access and processing of the data

     apt-get install git-annex-standalone python-mvpa2 python-nibabel fslview afni

and to generate/manipulate stimuli

     apt-get install handbrake-cli libav-tools
