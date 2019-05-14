# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

set -e

lg=$1  # input language

# data path
MAIN_PATH=$PWD
TOOLS_PATH=$PWD/tools

# tools
MOSES_DIR=$TOOLS_PATH/mosesdecoder
FASTBPE_DIR=$TOOLS_PATH/fastBPE
FASTBPE=$FASTBPE_DIR/fast
WMT16_SCRIPTS=$TOOLS_PATH/wmt16-scripts
FASTALIGN_DIR=$TOOLS_PATH/fast_align
FASTALIGN=$FASTALIGN_DIR/build/fast_align

# tools path
mkdir -p $TOOLS_PATH

#
# Download and install tools
#

cd $TOOLS_PATH

# Download Moses
if [ ! -d "$MOSES_DIR" ]; then
  echo "Cloning Moses from GitHub repository..."
  git clone https://github.com/moses-smt/mosesdecoder.git
fi

# Download fastBPE
if [ ! -d "$FASTBPE_DIR" ]; then
  echo "Cloning fastBPE from GitHub repository..."
  git clone https://github.com/glample/fastBPE
fi

# Compile fastBPE
if [ ! -f "$FASTBPE" ]; then
  echo "Compiling fastBPE..."
  cd fastBPE
  g++ -std=c++11 -pthread -O3 fastBPE/main.cc -IfastBPE -o fast
  cd ..
fi

# Download Sennrich's tools
if [ ! -d "$WMT16_SCRIPTS" ]; then
  echo "Cloning WMT16 preprocessing scripts..."
  git clone https://github.com/rsennrich/wmt16-scripts.git
fi

# Download WikiExtractor
if [ ! -d $TOOLS_PATH/wikiextractor ]; then
    echo "Cloning WikiExtractor from GitHub repository..."
    git clone https://github.com/attardi/wikiextractor.git
fi

# Download Stanford-segmenter-2018-10-16
if [ ! -d $TOOLS_PATH/stanford-segmenter-2018-10-16 ]; then
    echo "Downloading stanford segmenter..."
    wget -c https://nlp.stanford.edu/software/stanford-segmenter-2018-10-16.zip
    unzip -K stanford-segmenter-2018-10-16.zip
fi

# Chinese segmenter
if ! ls $TOOLS_PATH/stanford-segmenter-* 1> /dev/null 2>&1; then
  echo "Stanford segmenter not found at $TOOLS_PATH/stanford-segmenter-*"
  echo "Please install Stanford segmenter in $TOOLS_PATH"
  exit 1
fi

# # Thai tokenizer
# if ! python -c 'import pkgutil; exit(not pkgutil.find_loader("pythainlp"))'; then
#   echo "pythainlp package not found in python"
#   echo "Please install pythainlp (pip install pythainlp)"
#   exit 1
# fi
# 

# Download fast_align
if [ ! -d "$FASTALIGN_DIR" ]; then
  echo "Cloning fast_align from GitHub repository..."
  git clone https://github.com/clab/fast_align.git
fi

# Compile fast_align
if [ ! -f "$FASTALIGN" ]; then
  echo "Compiling fast_align..."
  cd fast_align
  mkdir build
  cd build
  cmake ..
  make
  cd ../..
fi