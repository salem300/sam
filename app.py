from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Caller ID API Running"

@app.route("/search")
def search():
    number = request.args.get("number")

    if number == "966500000000":
        return jsonify({
            "success": True,
            "name": "محمد أحمد"
        })

    return jsonify({
        "success": False,
        "name": None
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
