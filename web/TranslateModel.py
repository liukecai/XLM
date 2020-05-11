#-*-coding:utf-8-*-

import os
import torch
import fastBPE
import argparse
import traceback

from src.utils import AttrDict
from src.utils import initialize_exp
from src.data.dictionary import Dictionary
from src.model.transformer import TransformerModel

def get_parser():
    parser = argparse.ArgumentParser(description="Translation Web")

    # main parameters
    parser.add_argument("--dump_path", type=str, default="./dumped/", help="Experiment dump path")
    parser.add_argument("--exp_name", type=str, default="", help="Experiment name")
    parser.add_argument("--exp_id", type=str, default="", help="Experiment ID")
    parser.add_argument("--batch_size", type=int, default=32, help="Number of sentences per batch")

    # model / output paths
    parser.add_argument("--model_path", type=str, default="", help="Model path")
    parser.add_argument("--output_path", type=str, default="", help="Output path")
    parser.add_argument("--data_path", type=str, default="")

    # parser.add_argument("--max_vocab", type=int, default=-1, help="Maximum vocabulary size (-1 to disable)")
    # parser.add_argument("--min_count", type=int, default=0, help="Minimum vocabulary count")

    # source language / target language
    parser.add_argument("--src_lang", type=str, default="", help="Source language")
    parser.add_argument("--tgt_lang", type=str, default="", help="Target language")

    return parser

class TranslateModel(object):
    def __init__(self):
        self.loaded_model = False
        self.encoder = None
        self.decoder = None
        self.logger = None
        self.params = get_parser().parse_args()
        self.model_params = None
        self.bpe = None

    def is_loaded(self):
        return self.loaded_model

    def load_model(self, web_params, model_path):
        if self.loaded_model:
            self.loaded_model = False
            self.encoder = None
            self.decoder = None
            self.params = get_parser().parse_args()
            self.model_params = None
            self.bpe = None
            self.logger.info("Reload model...")
        self.web_params_process(web_params)
        self.logger = initialize_exp(self.params)

        reloaded = torch.load(model_path)
        self.model_params = AttrDict(reloaded['params'])
        self.logger.info("Supported languages: %s" % ", ".join(self.model_params.lang2id.keys()))

        # update dictionary parameters
        for name in ['n_words', 'bos_index', 'eos_index', 'pad_index', 'unk_index', 'mask_index']:
            setattr(self.params, name, getattr(self.model_params, name))

        # build dictionary / build encoder / build decoder / reload weights
        self.logger.info("Loading encoder and decoder...")
        dico = Dictionary(reloaded['dico_id2word'], reloaded['dico_word2id'], reloaded['dico_counts'])
        self.encoder = TransformerModel(self.model_params, dico, is_encoder=True, with_output=True).cuda().eval()
        self.decoder = TransformerModel(self.model_params, dico, is_encoder=False, with_output=True).cuda().eval()
        self.encoder.load_state_dict(reloaded['encoder'])
        self.decoder.load_state_dict(reloaded['decoder'])

        self.logger.info("Loading bpe...")
        self.bpe = fastBPE.fastBPE(os.path.join(self.params.data_path, "codes"),
                          os.path.join(self.params.data_path, "vocab.%s-%s" % (self.params.src_lang, self.params.tgt_lang)))

        self.loaded_model = True
        self.logger.info("Load model success.")

    def web_params_process(self, web_params):
        self.params.exp_name = web_params['exp_name']
        self.params.exp_id = web_params['exp_id']
        self.params.batch_size = int(web_params['batch_size'])
        self.params.model_path = web_params['model_path']
        self.params.src_lang = web_params['src_lang']
        self.params.tgt_lang = web_params['tgt_lang']

        self.params.data_path = os.path.join("data", "processed", "%s-%s" % (self.params.src_lang, self.params.tgt_lang))
