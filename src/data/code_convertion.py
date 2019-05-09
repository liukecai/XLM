# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
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


def load_dict(params, data):
    assert len(params.langs) == 2, "Need src and tgt two languages"

    src_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[0])
    tgt_dict_path = os.path.join(params.data_path, "vocab.%s" % params.langs[1])
    src_para_dict_path = os.path.join(params.data_path,
                                      "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[0]))
    tgt_para_dict_path = os.path.join(params.data_path,
                                      "dict.%s-%s.%s" % (params.langs[0], params.langs[1], params.langs[1]))

    assert os.path.isfile(src_dict_path) and os.path.isfile(tgt_dict_path) \
           and os.path.isfile(src_para_dict_path) and os.path.isfile(tgt_para_dict_path)

    from .dictionary import Dictionary

    logger.info("Read source monolingual vocabulary...")
    src_vocab = Dictionary.read_vocab(src_dict_path)
    data["src_vocab"] = src_vocab

    logger.info("Read target monolingual vocabulary...")
    tgt_vocab = Dictionary.read_vocab(tgt_dict_path)
    data["tgt_vocab"] = tgt_vocab

    logger.info("Read source parallel dictionary...")
    data["src_para_dict"] = load_para_dict(src_para_dict_path)

    logger.info("Read target parallel dictionary...")
    data["tgt_para_dict"] = load_para_dict(tgt_para_dict_path)