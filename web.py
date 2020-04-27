import platform
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

    result = content['text']
    return jsonify({"result": result}), 200


@app.route("/load", methods=["POST"])
def load_model():
    params = {"exp_name": request.form["exp_name"],
                "exp_id": request.form["exp_id"],
                "batch_size": request.form["batch_size"],
                "model_path": request.form["model_path"],
                "src_lang": request.form["src_lang"],
                "tgt_lang": request.form["tgt_lang"]}

    return jsonify({"info":"success"}), 200

if __name__ == "__main__":
    app.run()