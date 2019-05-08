# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from src.data.dictionary import Dictionary
import io
import numpy as np
import sys
import xlwt


def printCodesInChars(codes, dict):
    nRows , nCols = codes.shape
    for iRow in range(nRows):
        for iCol in range(nCols):
            print(dict[codes[iRow][iCol]], end=' ')
        print()

def saveCodesInCharsInExcel(codes, dict, ofilename):
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
            sheets[iData].write(iRow, iColInExcel, dict[codes[iRow][iCol]])
    writebook.save(ofilename)

def mytest20190508():
    dict = Dictionary.read_vocab('data/processed/en-zh/vocab.en-zh')
    dataToConvert = np.loadtxt(sys.argv[1], np.int32)

    printCodesInChars(dataToConvert, dict)
    saveCodesInCharsInExcel(dataToConvert, dict, sys.argv[1] + ".xls")

# https://www.cnblogs.com/feng18/p/5646925.html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
mytest20190508()