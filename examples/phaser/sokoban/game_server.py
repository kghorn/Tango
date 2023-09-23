from flask import Flask,render_template,send_file

app = Flask(__name__)

@app.route("/")
def game():
    import os
    return render_template("webpage.html")

@app.route("/img/<imagefile>")
def image(imagefile):
    return send_file(f"static/img/{imagefile}",mimetype='image/png')

@app.route("/src/<sourcefile>")
def source(sourcefile):
    return send_file(f"static/src/{sourcefile}",mimetype='text/javascript')

if __name__ == "__main__":
    app.run()