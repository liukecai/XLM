MOSES=tools/mosesdecoder
REPLACE_UNICODE_PUNCT=$MOSES/scripts/tokenizer/replace-unicode-punctuation.perl
NORM_PUNC=$MOSES/scripts/tokenizer/normalize-punctuation.perl
REM_NON_PRINT_CHAR=$MOSES/scripts/tokenizer/remove-non-printing-char.perl
TOKENIZER=$MOSES/scripts/tokenizer/tokenizer.perl
INPUT_FROM_SGM=$MOSES/scripts/ems/support/input-from-sgm.perl

EN_PREPROCESSING="$REPLACE_UNICODE_PUNCT | $NORM_PUNC -l en | $REM_NON_PRINT_CHAR | $TOKENIZER -l en -no-escape -threads 28"
ZH_PREPROCESSING="$REPLACE_UNICODE_PUNCT | $NORM_PUNC -l zh | $REM_NON_PRINT_CHAR | $TOKENIZER -l zh -no-escape -threads 28"

SEGMENTER_DIR=tools/stanford-segmenter-2018-10-16
SEGMENTER=$SEGMENTER_DIR/segment.sh

eval "cat data/para/en-zh/casia2015.shuffle.en | $EN_PREPROCESSING > data/para/en-zh/casia2015_en.tok.shuffle.txt"
eval "cat data/para/en-zh/casia2015.shuffle.zh | $ZH_PREPROCESSING > data/para/en-zh/casia2015_zh.tok.shuffle.txt"

$SEGMENTER ctb data/para/en-zh/casia2015_zh.tok.shuffle.txt UTF-8 0 > data/para/en-zh/casia2015_zh.seg.shuffle.txt

cd data/para/en-zh/

python split_by_rate.py casia2015_en.tok.shuffle.txt casia2015_zh.seg.shuffle.txt