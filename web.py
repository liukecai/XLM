import os
import platform
import traceback
from web.TranslateModel import TranslateModel
from flask import Flask, render_template, jsonify, request

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

MODEL = TranslateModel()

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

    if not MODEL.is_loaded():
        return jsonify({"info": "failed", "reason": "Model not loaded."}), 500

    result = content['text']
    return jsonify({"info": "success", "result": result}), 200


@app.route("/load", methods=["POST"])
def load_model():
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

    try:
        MODEL.load_model(params, model_path)
    except Exception as err:
        MODEL.logger.info(traceback.format_exc()) # print full exception stack
        return jsonify({"info": "failed", "reason": "Load error: %s" % err}), 500

    return jsonify({"info": "success"}), 200


if __name__ == "__main__":
    app.run()