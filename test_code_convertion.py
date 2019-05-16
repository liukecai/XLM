# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from src.data.dictionary import Dictionary
from src.data.code_convertion import ConverterBPE2BPE
from src.utils import bool_flag
from src.data.code_convertion import load_para_dict, convert_number_to_prob
from concurrent.futures import ProcessPoolExecutor
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
                lan0_dict_tree[tmp[0]][0].append(tmp[1])
                lan0_dict_tree[tmp[0]][1].append(int(tmp[2]))
            else:
                lan0_dict_tree[tmp[0]] = [[tmp[1]], [int(tmp[2])]]
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
                lan1_dict_tree[tmp[0]][0].append(tmp[1])
                lan1_dict_tree[tmp[0]][1].append(int(tmp[2]))
            else:
                lan1_dict_tree[tmp[0]] = [[tmp[1]], [int(tmp[2])]]
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

    return lan0_dict_tree, lan1_dict_tree


def mytest20190512_num_covert_prob(lan0_dict, lan1_dict):
    for key in lan0_dict.keys():
        if len(lan0_dict[key][0]) != len(lan0_dict[key][1]):
            print(key)
            print("Content length: %d Prob length: %d" % (len(lan0_dict[key][0]), len(lan0_dict[key][1])))
            continue
        p0 = np.array(lan0_dict[key][1])
        p0 = p0/np.sum(p0)

        # softmax
        p0 = np.exp(p0)/np.sum(np.exp(p0))

        lan0_dict[key][1] = p0
    for key in lan1_dict.keys():
        if len(lan1_dict[key][0]) != len(lan1_dict[key][1]):
            print(key)
            print("Content length: %d Prob length: %d" % (len(lan1_dict[key][0]), len(lan1_dict[key][1])))
            continue
        p1 = np.array(lan1_dict[key][1])
        p1 = p1/np.sum(p1)

        # softmax
        p1 = np.exp(p1)/np.sum(np.exp(p1))

        lan1_dict[key][1] = p1

    print()

import random
def mytest20190512_select_word(lan_dict, word):
    if lan_dict.has_subtrie(word) or lan_dict.has_key(word):
        keys = lan_dict.keys(word)
        index = random.randint(0, len(keys) - 1)
        key = keys[index]

        index_w = np.random.choice([x for x in range(len(lan_dict[key][1]))], p = lan_dict[key][1])
        return key, lan_dict[key][0][index_w]


def mytest20190513_multiprocess_load_data():
    parser = get_parser()
    params = parser.parse_args()
    check_data_params(params)

    lan0_para_dict_path = os.path.join(params.data_path,
                                       "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[0]))
    lan1_para_dict_path = os.path.join(params.data_path,
                                       "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[1]))

    lan0_dict = None
    lan1_dict = None

    # Need run with main
    print("Start multi-process...")
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = executor.map(load_para_dict, [lan0_para_dict_path, lan1_para_dict_path])
        results = list(results)
        lan0_dict = results[0]
        lan1_dict = results[1]

    print("lan0 dict length: %d, lan1 dict length: %d" % (len(lan0_dict), len(lan1_dict)))

    if lan0_dict.has_subtrie("s") or lan0_dict.has_key("s"):
        print(lan0_dict.items("s"))
        print(lan0_dict.items("sa"))
        print(lan0_dict.items("se"))

    print()
    if lan1_dict.has_subtrie("学") or lan1_dict.has_key("学"):
        print(lan1_dict.items("学"))
        print(lan1_dict.items("学生"))
    return lan0_dict, lan1_dict


def mytest20190515_convertOneList2Lan():
    parser = get_parser()
    params = parser.parse_args()
    check_data_params(params)
    converter = ConverterBPE2BPE(params)
    inputList = ['sin@@', 'gle', 'alter@@', 'red@@', 'red@@', 'ST@@', '能', '曾@@', 'able', '负@@', '载']
    print(converter.convertOneList2Lan(inputList,'zh'))
    print(converter.convertOneList2Lan(inputList, 'en'))
    inputList = ['sin@@', 'gle', 'alter@@', 'red@@', 'red@@', 'stu@@', '能', '曾@@', 'able', '负@@', '载']
    print(converter.convertOneList2Lan(inputList,'zh'))
    print(converter.convertOneList2Lan(inputList, 'en'))

    inputList = ['评定', '摘@@', '摘@@', '/', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@', '周@@']
    print(converter.convertOneList2Lan(inputList, 'zh'))
    print(converter.convertOneList2Lan(inputList, 'en'))


if __name__ == "__main__":
    # https://www.cnblogs.com/feng18/p/5646925.html
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
    # mytest20190508()
    # mytest20190509()
    # lan0_dict, lan1_dict = mytest20190512()

    mytest20190515_convertOneList2Lan()

    # ProcessPoolExecutor need run with main
    lan0_dict, lan1_dict = mytest20190513_multiprocess_load_data()
    convert_number_to_prob(lan0_dict)
    convert_number_to_prob(lan1_dict)

    for _ in range(5):
        for w in ["se", "al", "bl"]:
            select_word, new_word = mytest20190512_select_word(lan0_dict, w)
            print(select_word, " ", new_word)

        for w in ["我", "学", "水"]:
            select_word, new_word = mytest20190512_select_word(lan1_dict, w)
            print(select_word, " ", new_word)

        print()