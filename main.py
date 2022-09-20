import re
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
# from rushee import Rushee
from pydantic import create_model
app = Flask(__name__)

def swap(Rushee1, Rushee2):
    pass
def drop(Rushee1):
    pass
def jump():
    pass
def strike(Rushee1):
    pass
def set_pc():
    pass
def lock_pc():
    pass
def save():
    pass

rushees = []
def _create_rushees(df: pd.DataFrame) -> list:
    rushees.clear()
    # using create_model to create a model dynamically based on the columns of the dataframe
    for i, row in df.iterrows():
        rushee = create_model('Rushee', **{col: (str, ...) for col in df.columns})
        rushees.append(rushee(**row.to_dict()))
        print(rushee.__fields__.keys())
    return rushees
    
df = pd.DataFrame

@app.route('/vm2')
def vm2():
    return render_template('vm2.html', data=list(df.values.flatten()))


@app.route('/', methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        df = pd.read_csv(request.form["myfile"])
        df['strike'] = 0
        middle = int(len(df.values) / 2)
        rushees = _create_rushees(df)
        row = list(df.columns)
        row.remove('strike')
        return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)




if __name__ == '__main__':
    app.run(debug=True)