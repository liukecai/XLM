set -e

SRC=en
TGT=zh

N_THREADS=28

MAIN_PATH=$PWD
DATA_PATH=$PWD/data
TOOLS_PATH=$PWD/tools

# moses
MOSES=$TOOLS_PATH/mosesdecoder
REPLACE_UNICODE_PUNCT=$MOSES/scripts/tokenizer/replace-unicode-punctuation.perl
NORM_PUNC=$MOSES/scripts/tokenizer/normalize-punctuation.perl
REM_NON_PRINT_CHAR=$MOSES/scripts/tokenizer/remove-non-printing-char.perl
TOKENIZER=$MOSES/scripts/tokenizer/tokenizer.perl
INPUT_FROM_SGM=$MOSES/scripts/ems/support/input-from-sgm.perl

# stanford segmenter
SEGMENTER_DIR=$TOOLS_PATH/stanford-segmenter-*
SEGMENTER=$SEGMENTER_DIR/segment.sh

FASTALIGN_PATH=$TOOLS_PATH/fast_align
FASTALIGN=$FASTALIGN_PATH/build/fast_align
ATOOLS=$FASTALIGN_PATH/build/atools

FASTALIGN_DATA_PATH=$DATA_PATH/fast_align
FASTALIGN_PROCESS_PATH=$DATA_PATH/processed/fast_align

mkdir -p $FASTALIGN_DATA_PATH
mkdir -p $FASTALIGN_PROCESS_PATH

FASTALIGN=$TOOLS_PATH/fast_align/build/fast_align

# fast align process python file
READ_FAST_ALIGN_DATA=$MAIN_PATH/ourCode/read_fast_align_data.py
RANDOM_SHUFFLE=$MAIN_PATH/ourCode/random_shuffle.py
CONCATE=$MAIN_PATH/ourCode/concate.py
ALIGN_DICT=$MAIN_PATH/ourCode/align_word.py

echo "Read all parallel files..."
python $READ_FAST_ALIGN_DATA $FASTALIGN_DATA_PATH $FASTALIGN_PROCESS_PATH $SRC $TGT
echo "Random shuffle all parallel files..."
python $RANDOM_SHUFFLE $FASTALIGN_PROCESS_PATH/all.$SRC $FASTALIGN_PROCESS_PATH/all.$TGT

SRC_PREPROCESSING="$REPLACE_UNICODE_PUNCT | $NORM_PUNC -l $SRC | $REM_NON_PRINT_CHAR | $TOKENIZER -l $SRC -no-escape -threads $N_THREADS"
TGT_PREPROCESSING="$REPLACE_UNICODE_PUNCT | $NORM_PUNC -l $TGT | $REM_NON_PRINT_CHAR | $TOKENIZER -l $TGT -no-escape -threads $N_THREADS"

echo "Tokenizer all data..."
eval "cat $FASTALIGN_PROCESS_PATH/all.$SRC.shuffle | $SRC_PREPROCESSING > $FASTALIGN_PROCESS_PATH/all.tok.$SRC"
eval "cat $FASTALIGN_PROCESS_PATH/all.$TGT.shuffle | $TGT_PREPROCESSING > $FASTALIGN_PROCESS_PATH/all.tok.$TGT"

echo "Chinese segment..."
$SEGMENTER ctb $FASTALIGN_PROCESS_PATH/all.tok.$TGT UTF-8 0 > $FASTALIGN_PROCESS_PATH/all.seg.$TGT

echo "Concate $SRG and $TGT to one file..."
python $CONCATE $FASTALIGN_PROCESS_PATH/all.tok.$SRC $FASTALIGN_PROCESS_PATH/all.seg.$TGT $FASTALIGN_PROCESS_PATH/all.$SRC-$TGT
python $CONCATE $FASTALIGN_PROCESS_PATH/all.seg.$TGT $FASTALIGN_PROCESS_PATH/all.tok.$SRC $FASTALIGN_PROCESS_PATH/all.$TGT-$SRC

echo "Fast align $SRC-$TGT..."
$FASTALIGN -i $FASTALIGN_PROCESS_PATH/all.$SRC-$TGT -d -o -v > $FASTALIGN_PROCESS_PATH/forward.$SRC-$TGT.align
$FASTALIGN -i $FASTALIGN_PROCESS_PATH/all.$SRC-$TGT -d -o -v -r > $FASTALIGN_PROCESS_PATH/reverse.$SRC-$TGT.align
$ATOOLS -i $FASTALIGN_PROCESS_PATH/forward.$SRC-$TGT.align -j $FASTALIGN_PROCESS_PATH/reverse.$SRC-$TGT.align -c grow-diag-final-and > $FASTALIGN_PROCESS_PATH/final.$SRC-$TGT.align

echo "Fast align $TGT-$SRC..."
$FASTALIGN -i $FASTALIGN_PROCESS_PATH/all.$TGT-$SRC -d -o -v > $FASTALIGN_PROCESS_PATH/forward.$TGT-$SRC.align
$FASTALIGN -i $FASTALIGN_PROCESS_PATH/all.$TGT-$SRC -d -o -v -r > $FASTALIGN_PROCESS_PATH/reverse.$TGT-$SRC.align
$ATOOLS -i $FASTALIGN_PROCESS_PATH/forward.$TGT-$SRC.align -j $FASTALIGN_PROCESS_PATH/reverse.$TGT-$SRC.align -c grow-diag-final-and > $FASTALIGN_PROCESS_PATH/final.$TGT-$SRC.align


echo "Generate dict..."
python $ALIGN_DICT $FASTALIGN_PROCESS_PATH/all.$SRC-$TGT $FASTALIGN_PROCESS_PATH/final.$SRC-$TGT.align $FASTALIGN_PROCESS_PATH/dict.$SRC-$TGT.$SRC
python $ALIGN_DICT $FASTALIGN_PROCESS_PATH/all.$TGT-$SRC $FASTALIGN_PROCESS_PATH/final.$TGT-$SRC.align $FASTALIGN_PROCESS_PATH/dict.$SRC-$TGT.$TGT