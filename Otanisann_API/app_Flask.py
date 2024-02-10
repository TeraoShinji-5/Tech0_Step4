from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/double", methods=["POST"])
def double_number():
    data = request.json
    number = data["number"]
    return jsonify({"result": number * 2})



@app.route("/otanisann", methods=["POST"])
def altitude_otanisann():
    data = request.json
    altitude = data["altitude"]
    ohtani_height = 1.97
    otanisann = round(float(altitude)/ohtani_height)
    return jsonify({"result": otanisann})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
