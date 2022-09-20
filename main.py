from glob import glob
import re
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
# from rushee import Rushee
from pydantic import create_model
app = Flask(__name__)
df = pd.DataFrame()
middle = 0
row = []

def swap(Rushee1, Rushee2):
    global df
    r1_idx = -1
    r2_idx = -1
    #iterate through df to find rushee1 and rushee2 whose ranks are Rushee1 and Rushee2
    for index, row in df.iterrows():
        if row['Rank'] == Rushee1:
            r1_idx = index
        if row['Rank'] == Rushee2:
            r2_idx = index
    #swap the ranks of rushee1 and rushee2
    row1, row2 = df.iloc[r1_idx], df.iloc[r2_idx]
    temp = row1.copy()
    df.iloc[r1_idx] = row2
    df.iloc[r2_idx] = temp
    
def drop(Rushee1, location):
    global df
    # create an empty dataframe with the same columns as df
    temp_df = pd.DataFrame(columns=df.columns)
    # add len(df) blank rows to temp_df
    temp_df = temp_df.append([{} for i in range(len(df))], ignore_index=True)
    r1_idx = -1
    for index, row in df.iterrows():
        if row['Rank'] == Rushee1:
            r1_idx = index
    
    temp_df_indices = [i for i in range(len(df))]
    df_indices = [i for i in range(len(df))]
    
    #everybody above rushee
    for idx in range(0, r1_idx):
        temp_df.iloc[idx] = df.iloc[idx]
        temp_df_indices.remove(idx)
        df_indices.remove(idx)
    
    #rushee
    temp_df.iloc[location - 1] = df.iloc[r1_idx]
    temp_df_indices.remove(location - 1)
    df_indices.remove(r1_idx)
    
    #everybody below rushee
    for idx in range(location, len(df)):
        temp_df.iloc[idx] = df.iloc[idx]
        temp_df_indices.remove(idx)
        df_indices.remove(idx)
        
    #everybody locked 
    for idx in range(len(df)):
        if (df.iloc[idx]['Strikes'] == 2):
            temp_df.iloc[idx] = df.iloc[idx]
            temp_df_indices.remove(idx)
            df_indices.remove(idx)
    
    #everbody else
    for temp_idx, df_idx in zip(temp_df_indices, df_indices):
        temp_df.iloc[temp_idx] = df.iloc[df_idx]
    
    df = temp_df
    
def jump(Rushee1, location):
    global df
    # create an empty dataframe with the same columns as df
    temp_df = pd.DataFrame(columns=df.columns)
    # add len(df) blank rows to temp_df
    temp_df = temp_df.append([{} for i in range(len(df))], ignore_index=True)
    r1_idx = -1
    for index, row in df.iterrows():
        if row['Rank'] == Rushee1:
            r1_idx = index
    
    temp_df_indices = [i for i in range(len(df))]
    df_indices = [i for i in range(len(df))]
    
    #everybody above location
    for idx in range(0, location - 1):
        temp_df.iloc[idx] = df.iloc[idx]
        temp_df_indices.remove(idx)
        df_indices.remove(idx)
    
    #rushee
    temp_df.iloc[location - 1] = df.iloc[r1_idx]
    temp_df_indices.remove(location - 1)
    df_indices.remove(r1_idx)
    
    #everybody below rushee
    for idx in range(r1_idx + 1, len(df)):
        temp_df.iloc[idx] = df.iloc[idx]
        temp_df_indices.remove(idx)
        df_indices.remove(idx)
        
    #everybody locked 
    for idx in range(len(df)):
        if (df.iloc[idx]['Strikes'] == 2):
            temp_df.iloc[idx] = df.iloc[idx]
            temp_df_indices.remove(idx)
            df_indices.remove(idx)
    
    #everbody else
    for temp_idx, df_idx in zip(temp_df_indices, df_indices):
        temp_df.iloc[temp_idx] = df.iloc[df_idx]
    
    df = temp_df   


def strike(Rushee1):
    global df
    r1_idx = -1
    for index, row in df.iterrows():
        if row['Rank'] == Rushee1:
            r1_idx = index
    df.at[r1_idx, 'Strikes'] += 1
def set_pc():
    pass
def lock_pc(size):
    global df
    for idx in range(0, size):
        df.at[idx, 'Strikes'] = 2
    
def save():
    global df
    # get current time
    from datetime import datetime
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(f'{time}.csv', index=False)

@app.route('/', methods=["GET","POST"])
def index():
    global df
    global middle
    global row
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        if request.form.get("myfile", None):
            df = pd.read_csv(request.form["myfile"])
            if "Strikes" not in df.columns:
                df['Strikes'] = 0
            middle = int(len(df.values) / 2)
            # rushees = _create_rushees(df)
            row = list(df.columns)
            row.remove('Strikes')
            return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
        else:
            if request.form["motion"] == "swap":
                strike(int(request.form["rushee1"]))
                strike(int(request.form["optional"]))
                swap(int(request.form["rushee1"]), int(request.form["optional"]))
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
            if request.form["motion"] == "drop":
                strike(int(request.form["rushee1"]))
                drop(int(request.form["rushee1"]), int(request.form["optional"]))
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
            if request.form["motion"] == "jump":
                strike(int(request.form["rushee1"]))
                jump(int(request.form["rushee1"]), int(request.form["optional"]))
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
            if request.form["motion"] == "strike":
                strike(int(request.form["rushee1"]))
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
            if request.form["motion"] == "lock":
                lock_pc(int(request.form["rushee1"]))
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
            if request.form["motion"] == "save":
                save()
                return render_template("vm2.html", rows=row, rushees=list(df.values), middle=middle)
                

if __name__ == '__main__':
    app.run(debug=True)