from flask import Flask, render_template, request, redirect, url_for, flash
import pandas
app = Flask(__name__)



@app.route('/', methods=["POST"])
def index():
    pass


if __name__ == '__main__':
    app.run(debug=True)