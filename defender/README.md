# MLSEC 2021

Install Ember using `pip install git+https://github.com/elastic/ember.git`. More information on
Ember installation can be found on their Github repository https://github.com/elastic/ember.

## Usage

### Training

### Predicting

## Notes

Change ember's feature.py to print to stderr and flush the buffer immediately after.

On Mac, if you get the following error `OSError: dlopen(/usr/local/lib/python3.9/site-packages/lightgbm/lib_lightgbm.so, 6): Library not loaded: /usr/local/opt/libomp/lib/libomp.dylib`, you may have to install LLVM's OpenMP runtime library using `brew install libomp`.

If you get encoding errors when converting PEs to JSONs, change the py module file \_io/capture.py line 43 from "UTF-8" to "iso-8859-15".

