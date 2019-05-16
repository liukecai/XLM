# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import fastBPE
import os
import random
import re
import xlwt
import numpy as np
import pygtrie as trie
from .dictionary import Dictionary, BOS_WORD, EOS_WORD, PAD_WORD, UNK_WORD
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


IS_DIGIT = re.compile(r'^[-+]?\d+\.?\d*|[-+]?\d+$')
IS_ENGLISH = re.compile(r'^[a-zA-Z]+$')
def determineWordType(word):
    if IS_DIGIT.fullmatch(word) :
        return 'nu'
    elif IS_ENGLISH.match(word) :
        return 'en'
    return 'zh'


def list2words(inputTupleList):
    wordList = []
    cntList = []
    for word, wdCntList in inputTupleList:
        wordList.extend(wdCntList[0])
        cntList.extend(wdCntList[1])
    p1 = np.array(cntList)
    p1 = p1 / np.sum(p1)
    index_w = np.random.choice([x for x in range(len(wordList))], p=p1)
    return wordList[index_w]


class ConverterBPE2BPE():
    def __init__(self, params):
        assert len(params.langs) == 2, "Need two languages"
        lan0_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[0])
        lan1_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[1])
        all_dict_path = os.path.join(params.data_path, "vocab.%s-%s" % (params.langs[0], params.langs[1]))
        assert os.path.isfile(lan0_dict_path) and os.path.isfile(lan1_dict_path) and os.path.isfile(all_dict_path)
        logger.info("Read lan0 monolingual vocabulary...")
        self.lan0_vocab = Dictionary.read_vocab(lan0_dict_path)
        logger.info("Read lan1 monolingual vocabulary...")
        self.lan1_vocab = Dictionary.read_vocab(lan1_dict_path)
        logger.info("Read monolingual vocabulary for both languages...")
        self.all_vocab = Dictionary.read_vocab(all_dict_path)
        self.code_BOS_WORD = self.all_vocab.index(BOS_WORD)
        self.code_EOS_WORD = self.all_vocab.index(EOS_WORD)
        self.code_PAD_WORD = self.all_vocab.index(PAD_WORD)
        self.code_UNK_WORD = self.all_vocab.index(UNK_WORD)

        lan0_para_dict_path = os.path.join(params.data_path,
                                          "dict.%s-%s.%s.a%s" % (params.langs[0], params.langs[1], params.langs[0], 100))
        lan1_para_dict_path = os.path.join(params.data_path,
                                          "dict.%s-%s.%s.a%s" % (params.langs[0], params.langs[1], params.langs[1], 100))
        if params.debug_dict:
            lan0_para_dict_path = lan0_para_dict_path.replace('100', '1000')
            lan1_para_dict_path = lan1_para_dict_path.replace('100', '1000')
        assert os.path.isfile(lan0_para_dict_path) and os.path.isfile(lan1_para_dict_path)
        logger.info("Read parallel dictionary for language 0...")
        self.dict_lan0 = load_para_dict(lan0_para_dict_path)
        logger.info("Read parallel dictionary for language 1...")
        self.dict_lan1 = load_para_dict(lan1_para_dict_path)

        codes_path = os.path.join(params.data_path, "codes")
        self.bpe = fastBPE.fastBPE(codes_path, all_dict_path)

        # logger.info("Process parallel dictionary for language 0...")
        # convert_number_to_prob(self.dict_lan0)
        # logger.info("Process parallel dictionary for language 1...")
        # convert_number_to_prob(self.dict_lan1)


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


    def convertOneList2Lan(self, inputList, lan):
        iStart = 0
        output = ""
        preLan = None
        if lan == 'en':
            prefixTreeDict = self.dict_lan1
        else:
            prefixTreeDict = self.dict_lan0

        while iStart < len(inputList):
            iCurrent = iStart
            prefix = ""
            reCurrent = []
            rePre = []
            bEndWord = False

            while iCurrent < len(inputList):
                curWord = inputList[iCurrent]
                if curWord.endswith("@@"):
                    curWord = curWord.split("@@")[0]
                    if iCurrent == len(inputList) - 1:
                        bEndWord = True
                else:
                    bEndWord = True
                wordType = determineWordType(curWord)
                if wordType == 'nu' or wordType == lan:
                    if len(reCurrent) > 0:
                        output += list2words(reCurrent)
                    if preLan != None and preLan != wordType:
                        output += " "
                    output += curWord
                    if bEndWord == True:
                        output += " "
                    iStart = iCurrent + 1
                    preLan = wordType
                    break
                if preLan != None and preLan != wordType:
                    output += " "
                preLan = wordType
                prefix += curWord
                rePre = reCurrent
                if prefixTreeDict.has_key(prefix):
                    reCurrent = prefixTreeDict.items(prefix)
                    reCurrent = [ reCurrent[0] ]
                elif prefixTreeDict.has_subtrie(prefix):
                    reCurrent = prefixTreeDict.items(prefix)
                else:
                    reCurrent = []

                if not bEndWord and len(reCurrent) > 0 :
                    iCurrent += 1
                    continue
                if bEndWord and len(reCurrent) > 0 :
                    output += list2words(reCurrent)
                    output += " "
                    iStart = iCurrent + 1
                    break
                elif len(rePre) > 0:
                    output += list2words(rePre)
                    output += " "
                    iStart = iCurrent
                    break
                else:
                    output += prefix
                    output += " "
                    iStart = iCurrent + 1
                    break
        output = output.strip().split()
        output = " ".join(output)
        return output


    def convertCodes2Lan(self, codes, lan):
        nRows, nCols = codes.shape
        out_sentences = []
        for iCols in range(nCols):
            sentence = []
            for iRow in range(nRows):
                word_code = codes[iRow, iCols]
                if word_code == self.code_PAD_WORD or word_code == self.code_EOS_WORD or word_code == self.code_UNK_WORD or word_code == self.code_BOS_WORD :
                    continue
                sentence.append(self.all_vocab[word_code])
            out_sentence = self.convertOneList2Lan(sentence, lan)
            print(sentence)
            print(out_sentence)
            out_sentences.append(out_sentence)

        re = self.bpe.apply(out_sentences)

        return codes