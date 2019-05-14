# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import re
import xlwt
import numpy as np
import pygtrie as trie
from logging import getLogger
from concurrent.futures import ProcessPoolExecutor

logger = getLogger()

def load_para_dict(filename):
    # load dict to the trie
    para_dict = trie.CharTrie()
    dict_file = open(filename, mode="r", encoding="UTF-8")
    lines = dict_file.readlines()
    for line in lines:
        line = line.strip()
        if len(line) != 0:
            tmp = line.split()
            if para_dict.has_key(tmp[0]):
                para_dict[tmp[0]][0].append(tmp[1])
                para_dict[tmp[0]][1].append(int(tmp[2]))
            else:
                para_dict[tmp[0]] = [[tmp[1]], [int(tmp[2])]]
    dict_file.close()
    logger.info("Read %d words from the dictionary file." % len(lines))

    return para_dict


def convert_number_to_prob(para_dict):
    # from the trie covert the number to probability
    for key in para_dict.keys():
        assert len(para_dict[key][0]) == len(para_dict[key][1])
        p = np.array(para_dict[key][1])
        p = p / np.sum(p)
        # softmax
        p = np.exp(p) / np.sum(np.exp(p))
        para_dict[key][1] = p


class ConverterBPE2BPE():
    def __init__(self, params):
        assert len(params.langs) == 2, "Need two languages"
        lan0_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[0])
        lan1_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[1])
        all_dict_path = os.path.join(params.data_path, "vocab.%s-%s" % (params.langs[0], params.langs[1]))
        assert os.path.isfile(lan0_dict_path) and os.path.isfile(lan1_dict_path) and os.path.isfile(all_dict_path)
        from .dictionary import Dictionary
        logger.info("Read lan0 monolingual vocabulary...")
        self.lan0_vocab = Dictionary.read_vocab(lan0_dict_path)
        logger.info("Read lan1 monolingual vocabulary...")
        self.lan1_vocab = Dictionary.read_vocab(lan1_dict_path)
        logger.info("Read monolingual vocabulary for both languages...")
        self.all_vocab = Dictionary.read_vocab(all_dict_path)

        lan0_para_dict_path = os.path.join(params.data_path,
                                          "dict.%s-%s.%s.a%s" % (params.langs[0], params.langs[1], params.langs[0], 100))
        lan1_para_dict_path = os.path.join(params.data_path,
                                          "dict.%s-%s.%s.a%s" % (params.langs[0], params.langs[1], params.langs[1], 100))
        assert os.path.isfile(lan0_para_dict_path) and os.path.isfile(lan1_para_dict_path)
        logger.info("Read parallel dictionary for language 0...")
        self.dict_lan0 = load_para_dict(lan0_para_dict_path)
        logger.info("Read parallel dictionary for language 1...")
        self.dict_lan1 = load_para_dict(lan1_para_dict_path)

        logger.info("Process parallel dictionary for language 0...")
        convert_number_to_prob(self.dict_lan0)
        logger.info("Process parallel dictionary for language 1...")
        convert_number_to_prob(self.dict_lan1)

        self.IS_DIGIT = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')

    def saveCodesInCharsInExcel(self, codes, ofilename):
        writebook = xlwt.Workbook()
        sheets = []
        sheet = writebook.add_sheet('data')
        sheets.append(sheet)
        nRows , nCols = codes.shape
        for iRow in range(nRows):
            for iCol in range(nCols):
                iData = int( iCol / 256 )
                if (len(sheets) <= iData) :
                    sheets.append(writebook.add_sheet('data' + str(iData)))
                iColInExcel = iCol % 256
                sheets[iData].write(iRow, iColInExcel, self.all_vocab[codes[iRow][iCol]])
        writebook.save(ofilename)

    def convertCodes2Lan(self, codes, lan):
        nRows, nCols = codes.shape
        sentences = []
        for iCols in range(nCols):
            sentence = []
            for iRow in range(nRows):
                sentence.append(self.all_vocab[codes[iRow, iCols]])
            sentences.append(sentence)

        # covert_dict used save the concate word, save as:
        # {(1,2,3):(prefix, concate_word)}
        # (1,2,3): the 1st sentence, concate word start from 2ed index, end with 3rd index
        covert_dict = {}
        for sen_index, sen in enumerate(sentences):
            long_words = ""
            prefix = ""
            continue_flag = False
            start_word_index = 0
            for word_index, word in enumerate(sen):

                if word.endswith("@@"):
                    if not continue_flag:
                        start_word_index = word_index
                        prefix = word
                    word = word.split("@@")[0]
                    long_words += word
                    continue_flag = True
                else:
                    if continue_flag:
                        long_words += word
                        continue_flag = False
                    if not continue_flag and len(long_words) != 0:
                        covert_dict[(sen_index, start_word_index, word_index)] = (prefix, long_words)
                        long_words = ""


                # if self.IS_DIGIT.match(word):
                #     print("dg", end=" ")
                # elif word in ['<s>','</s>','<pad>','<unk>']:
                #     print("sp", end=" ")
                # elif word in "~!@#$%^&*()_+<>?:,./;’，。、‘：“《》？~！@#￥%……（）":
                #     print("pu", end=" ")
                # elif word in self.lan0_vocab:
                #     print(self.params.id2lang[0], end=" ")
                # elif word in self.lan1_vocab:
                #     print(self.params.id2lang[1], end=" ")
                # else:
                #     print("UK", end=" ")
            print()

        print(sentences)

        return codes