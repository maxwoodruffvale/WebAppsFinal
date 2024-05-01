import flask as fk
import html
from flask import render_template
import logging

logging.basicConfig(level=logging.DEBUG)


app = fk.Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    else:
        return "you did it!" #post return, should eventually lead to suggested tutors page

if __name__ == "__main__":
    app.run(debug=True)