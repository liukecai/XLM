# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import xlwt
from logging import getLogger

logger = getLogger()

def load_para_dict(filename):
    para_dict = {}
    dict_file = open(filename, mode="r", encoding="UTF-8")
    lines = dict_file.readlines()
    for line in lines:
        line = line.strip()
        if len(line) != 0:
            tmp = line.split()
            if tmp[0] in para_dict.keys():
                para_dict[tmp[0]].append(tmp[1])
            else:
                para_dict[tmp[0]] = [tmp[1]]
    dict_file.close()
    logger.info("Read %d words from the dictionary file." % len(lines))

    return para_dict


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
                                          "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[0]))
        lan1_para_dict_path = os.path.join(params.data_path,
                                          "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[1]))
        assert os.path.isfile(lan0_para_dict_path) and os.path.isfile(lan1_para_dict_path)
        logger.info("Read parallel dictionary for language 0...")
        # self.dict_lan0 = load_para_dict(lan0_para_dict_path)
        logger.info("Read parallel dictionary for language 1...")
        # self.dict_lan1 = load_para_dict(lan1_para_dict_path)

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
        return codes