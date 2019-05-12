# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from src.data.dictionary import Dictionary
from src.data.code_convertion import ConverterBPE2BPE
from src.utils import bool_flag
import argparse
import io
import numpy as np
import os
import sys


def get_parser():
    parser = argparse.ArgumentParser(description="Language transfer")

    # data
    parser.add_argument("--data_path", type=str, default="",
                        help="Data path")
    parser.add_argument("--lgs", type=str, default="",
                        help="Languages (lg1-lg2-lg3 .. ex: en-fr-es-de)")
    # avoid degenerate
    parser.add_argument("--anti_degenerate", type=bool_flag, default=False,
                        help="Use this way for avoid degenerate")

    parser.add_argument("--data_file_to_convert", type=str, default="",
                        help="The name of the data file to be converted.")
    return parser


def check_data_params(params):
    """
    Check datasets parameters.
    """
    # data path
    assert os.path.isdir(params.data_path), params.data_path

    # check languages
    params.langs = params.lgs.split('-') if params.lgs != 'debug' else ['en']
    assert len(params.langs) == len(set(params.langs)) >= 1
    # assert sorted(params.langs) == params.langs
    params.id2lang = {k: v for k, v in enumerate(sorted(params.langs))}
    params.lang2id = {k: v for v, k in params.id2lang.items()}
    params.n_langs = len(params.langs)


def mytest20190508():
    parser = get_parser()
    params = parser.parse_args()
    check_data_params(params)
    converter = ConverterBPE2BPE(params)
    dataToConvert = np.loadtxt(params.data_file_to_convert, np.int32)

    converter.saveCodesInCharsInExcel(dataToConvert, params.data_file_to_convert + ".xls")
    dataConvertEn = converter.convertCodes2Lan(dataToConvert, 'en')
    dataConvertZh = converter.convertCodes2Lan(dataToConvert, 'zh')
    converter.saveCodesInCharsInExcel(dataConvertEn, params.data_file_to_convert + ".2en.xls")
    converter.saveCodesInCharsInExcel(dataConvertZh, params.data_file_to_convert + ".2zh.xls")


def mytest20190509():
    import fastBPE
    bpe = fastBPE.fastBPE("data/processed/en-zh/codes", "data/processed/en-zh/vocab.en-zh")
    re = bpe.apply(["Roasted barramundi fish", "Centrally managed over a client-server architecture"])
    print(re)


def mytest20190512():
    # https://github.com/google/pygtrie
    # pip install pygtrie
    import pygtrie as trie
    parser = get_parser()
    params = parser.parse_args()
    check_data_params(params)

    lan0_para_dict_path = os.path.join(params.data_path,
                                       "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[0]))
    lan1_para_dict_path = os.path.join(params.data_path,
                                       "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[1]))

    lan0_para_dict_file = open(lan0_para_dict_path, mode="r", encoding="UTF-8")
    lan1_para_dict_file = open(lan1_para_dict_path, mode="r", encoding="UTF-8")

    count = 0

    lan0_dict_tree = trie.CharTrie()
    lines = lan0_para_dict_file.readlines()
    for line in lines:
        if count == 10000:
            break
        count += 1
        line = line.strip()
        if len(line) != 0:
            tmp = line.split()
            if lan0_dict_tree.has_key(tmp[0]):
                lan0_dict_tree[tmp[0]].append(tmp[1])
            else:
                lan0_dict_tree[tmp[0]] = [tmp[1]]
    lan0_para_dict_file.close()

    count = 0

    lan1_dict_tree = trie.CharTrie()
    lines = lan1_para_dict_file.readlines()
    for line in lines:
        if count == 10000:
            break
        count += 1

        line = line.strip()
        if len(line) != 0:
            tmp = line.split()
            if lan1_dict_tree.has_key(tmp[0]):
                lan1_dict_tree[tmp[0]].append(tmp[1])
            else:
                lan1_dict_tree[tmp[0]] = [tmp[1]]
    lan1_para_dict_file.close()

    if lan0_dict_tree.has_subtrie("s") or lan0_dict_tree.has_key("s"):
        print(lan0_dict_tree.items("s"))
        print(lan0_dict_tree.items("sa"))
        print(lan0_dict_tree.items("se"))

    print()
    if lan0_dict_tree.has_subtrie("学") or lan1_dict_tree.has_key("学"):
        # don't need sys.stdout
        print(lan1_dict_tree.items("学"))
        print(lan1_dict_tree.items("学生"))


# https://www.cnblogs.com/feng18/p/5646925.html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
mytest20190508()
# mytest20190509()
# mytest20190512()