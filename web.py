import os
import torch
import argparse
import platform
import traceback

from flask import Flask, render_template, jsonify, request

from src.utils import AttrDict
from src.utils import initialize_exp
from src.data.dictionary import Dictionary
from src.model.transformer import TransformerModel

if platform.system() == 'windows':
    app = Flask(import_name=__name__,
                static_folder="web\\static",
                template_folder="web\\templates")
else:
    app = Flask(import_name=__name__,
                static_folder="web/static",
                template_folder="web/templates")

# cmd: set FLASK_ENV=development
# bash: export FLASK_ENV=development
app.debug = True

LOADED_MODEL = False
MODEL_ENCODER = None
MODEL_DECODER = None
LOGGER = None

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate():
    content = {
        "text": request.form["text"],
        "lang1": request.form["lang1"],
        "lang2": request.form["lang2"]
    }

    if LOADED_MODEL is False:
        return jsonify({"info": "failed", "reason": "Model not loaded."}), 500

    result = content['text']
    return jsonify({"info": "success", "result": result}), 200


@app.route("/load", methods=["POST"])
def load_model():
    # using global var
    global LOADED_MODEL
    global MODEL_ENCODER
    global MODEL_DECODER
    global LOGGER

    if LOADED_MODEL:
        LOADED_MODEL = False
        del MODEL_ENCODER
        del MODEL_DECODER
        LOGGER.info("Reload model...")

    params = {"exp_name": request.form["exp_name"],
                "exp_id": request.form["exp_id"],
                "batch_size": request.form["batch_size"],
                "model_path": request.form["model_path"],
                "src_lang": request.form["src_lang"],
                "tgt_lang": request.form["tgt_lang"]}

    model_path = os.path.join("./dumped", params["exp_name"], params["exp_id"], params["model_path"])
    if not os.path.isfile(model_path):
        return jsonify({"info": "failed", "reason": "Not found model."}), 500

    try:
        params["batch_size"] = int(params["batch_size"])
        assert params["batch_size"] > 0, "Batch size need greater than 0"
    except Exception as err:
        return jsonify({"info": "failed", "reason": "Batch size error: %s" % err}), 500

    params["dump_path"] = os.path.join("./dumped", "web")
    params = __params_process(params)

    try:
        __load_model(params, model_path)
    except Exception as err:
        LOGGER.info(traceback.format_exc()) # print full exception stack
        return jsonify({"info": "failed", "reason": "Load error: %s" % err}), 500

    LOADED_MODEL = True
    LOGGER.info("Load model success.")
    return jsonify({"info": "success"}), 200


def __load_model(params, model_path):
    global LOGGER
    LOGGER = initialize_exp(params)

    reloaded = torch.load(model_path)
    model_params = AttrDict(reloaded['params'])
    LOGGER.info("Supported languages: %s" % ", ".join(model_params.lang2id.keys()))

    # update dictionary parameters
    for name in ['n_words', 'bos_index', 'eos_index', 'pad_index', 'unk_index', 'mask_index']:
        setattr(params, name, getattr(model_params, name))

    # build dictionary / build encoder / build decoder / reload weights
    dico = Dictionary(reloaded['dico_id2word'], reloaded['dico_word2id'], reloaded['dico_counts'])
    encoder = TransformerModel(model_params, dico, is_encoder=True, with_output=True).cuda().eval()
    decoder = TransformerModel(model_params, dico, is_encoder=False, with_output=True).cuda().eval()
    encoder.load_state_dict(reloaded['encoder'])
    decoder.load_state_dict(reloaded['decoder'])

    global MODEL_ENCODER
    global MODEL_DECODER
    MODEL_ENCODER = encoder
    MODEL_DECODER = decoder


def __params_process(dic):
    parser = argparse.ArgumentParser(description="Translation Web")

    # main parameters
    parser.add_argument("--dump_path", type=str, default="./dumped/", help="Experiment dump path")
    parser.add_argument("--exp_name", type=str, default="", help="Experiment name")
    parser.add_argument("--exp_id", type=str, default="", help="Experiment ID")
    parser.add_argument("--batch_size", type=int, default=32, help="Number of sentences per batch")

    # model / output paths
    parser.add_argument("--model_path", type=str, default="", help="Model path")
    parser.add_argument("--output_path", type=str, default="", help="Output path")

    # parser.add_argument("--max_vocab", type=int, default=-1, help="Maximum vocabulary size (-1 to disable)")
    # parser.add_argument("--min_count", type=int, default=0, help="Minimum vocabulary count")

    # source language / target language
    parser.add_argument("--src_lang", type=str, default="", help="Source language")
    parser.add_argument("--tgt_lang", type=str, default="", help="Target language")

    params = parser.parse_args()

    params.exp_name = dic['exp_name']
    params.exp_id = dic['exp_id']
    params.batch_size = int(dic['batch_size'])
    params.model_path = dic['model_path']
    params.src_lang = dic['src_lang']
    params.tgt_lang = dic['tgt_lang']

    return params



if __name__ == "__main__":
    app.run()