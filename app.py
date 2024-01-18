
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    Dict = {"color": 25, "fruit": 56, "pet": 86}

    if request.method == 'POST':
        sum = 0
        name = request.form.get('name')

        for value in Dict.values():
            if name in Dict.keys():
                sum += value
                return render_template("index.html", sum=sum, name=name)
            pass
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)