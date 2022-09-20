from glob import glob
import re
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from scipy import stats
# from rushee import Rushee
from pydantic import create_model
app = Flask(__name__)
df = pd.DataFrame()
middle = 0
row = []
color_gradient = []
remove = 1

def hex_to_RGB(hex):
  ''' "#FFFFFF" -> [255,255,255] '''
  # Pass 16 to the integer function for change of base
  return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
  ''' [255,255,255] -> "#FFFFFF" '''
  # Components need to be integers for hex to make sense
  RGB = [int(x) for x in RGB]
  return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])

def color_dict(gradient):
  ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
  return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
  ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") '''
  # Starting and ending colors in RGB form
  s = hex_to_RGB(start_hex)
  f = hex_to_RGB(finish_hex)
  # Initilize a list of the output colors with the starting color
  RGB_list = [s]
  # Calcuate a color at each evenly spaced value of t from 1 to n
  for t in range(1, n):
    # Interpolate RGB vector for color at the current value of t
    curr_vector = [
      int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
      for j in range(3)
    ]
    # Add it to our list of output colors
    RGB_list.append(curr_vector)

  return color_dict(RGB_list)

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
        if (df.iloc[idx]['Strikes']["val"] == 2):
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
        if (df.iloc[idx]['Strikes']["val"] == 2):
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
    df.at[r1_idx, 'Strikes']["val"] += 1

def lock_pc(size):
    global df
    for idx in range(0, size):
        df.at[idx, 'Strikes']["val"] = 2
    
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
    global color_gradient
    global remove
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        if request.form.get("myfile", None):
            df = pd.read_csv(request.form["myfile"])
            if "Strikes" not in df.columns:
                df['Strikes'] = 0
            row = list(df.columns)
            row.remove('Strikes')

            # store columns 0 and 1 and the last column in a dataframe
            middle = df.iloc[:, 0:3]
            # drop columns 1 and 2
            df.drop(df.columns[0:3], axis=1, inplace=True)

            # print(middle)

            color_gradient = ["#ED5565", "#ED5A66", "#EE6068", "#EF666A", "#EF6C6C", 
                "#F0726D", "#F1786F", "#F27E71", "#F28473", "#F38A74", 
                "#F49076", "#F49678", "#F59C7A", "#F6A27B", "#F7A87D", 
                "#F7AE7F", "#F8B481", "#F9BA82", "#F9C084", "#FAC686", 
                "#FBCC88", "#FCD289", "#FCD88B", "#FDDE8D", "#FEE48F", 
                "#FFEA91", "#F5E791", "#EBE591", "#E2E391", "#D8E091", 
                "#CFDE91", "#C5DC91", "#BCD991", "#B2D792", "#A9D592", 
                "#9FD392", "#96D092", "#8CCE92", "#82CC92", "#79C992", 
                "#6FC792", "#66C593", "#5CC393", "#53C093", "#49BE93", 
                "#40BC93", "#36B993", "#2DB793", "#23B593", "#1AB394"]
            # iterate starting from the third column to the end
            for idx, name in enumerate(df):
                col_name = name
                # each val in name.value calcaulte its percentil
                col_val_with_color = []
                for val in df[name]:
                    p = stats.percentileofscore(df[name], val)
                    # calcaulte index of color relateive to color_gradient
                    idx_color = int((len(color_gradient) - 1) * (p / 100))
                    # append the value and its color
                    memo = {}
                    memo["val"] = val
                    memo["color"] = color_gradient[idx_color]
                    col_val_with_color.append(memo)
            
                # drop the column and add it again in the same position
                df.drop(col_name, axis=1, inplace=True)
                df.insert(idx, col_name, col_val_with_color)

            


            # add middle to the beginning of df
            df = pd.concat([middle, df], axis=1)
         
            middle = int(len(df.values) / 2)
            rushees_top = df.iloc[:middle]
            rushees_bottom = df.iloc[middle:]
            return render_template("vm2.html", rows=row, rushees1=rushees_top, rushees2=rushees_bottom, middle=middle, remove= -1 * remove)
        else:
            if request.form["motion"] == "swap":
                strike(int(request.form["rushee1"]))
                strike(int(request.form["optional"]))
                swap(int(request.form["rushee1"]), int(request.form["optional"]))
            if request.form["motion"] == "drop":
                strike(int(request.form["rushee1"]))
                drop(int(request.form["rushee1"]), int(request.form["optional"]))
            if request.form["motion"] == "jump":
                strike(int(request.form["rushee1"]))
                jump(int(request.form["rushee1"]), int(request.form["optional"]))
            if request.form["motion"] == "strike":
                strike(int(request.form["rushee1"]))
            if request.form["motion"] == "lock":
                lock_pc(int(request.form["rushee1"]))
            if request.form["motion"] == "save":
                save()
            
            rushees_top = df.iloc[:middle]
            rushees_bottom = df.iloc[middle:]
            return render_template("vm2.html", rows=row, rushees1=rushees_top, rushees2=rushees_bottom, middle=middle, remove= -1 * remove)


if __name__ == '__main__':
    app.run(debug=True)