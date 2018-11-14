# Totter
Discovering QWOP gaits with evolutionary computing.

## Installation

This project uses [Conda](https://conda.io/docs/user-guide/install/index.html) for dependency management.

### Linux

`conda env create -f environment.nix.yaml`

Linux systems require the `scrot` command to be available for the user running Totter.  
It can be installed with `apt-get`:

`sudo apt-get install scrot`

Linux systems require the `tesseract-ocr` package to be installed.

`sudo apt-get install tesseract-ocr`

### Windows

`conda env create -f environment.win.yml`

Install tesseract using one of the [UB Mannheim installers](https://github.com/UB-Mannheim/tesseract/wiki).
Make sure the tesseract executable is on the system PATH.

### OS X

`conda env create -f environment.mac.yml`

OS X requires the `tesseract` package to be installed:
`brew install tesseract`

## Running 

`source activate totter`

`python ...`

# Contributors
- Zach Jones (https://github.com/zachdj)
