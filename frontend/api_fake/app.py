from flask import Flask, request
from flask_cors import CORS
from random import choice

app = Flask(__name__)
CORS(app)

@app.route("/verificar_lixo", methods=["POST"])
def verificar_lixo():

    imagem = request.files.get("teste")

    if imagem is None:
        return "0"

    return str(choice([0,1]))


if __name__ == "__main__":
    app.run(debug=True)