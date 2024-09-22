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

def swap(Rushee1, Rushee2):
    global df
    r1_idx = -1
    r2_idx = -1
    #iterate through df to find rushee1 and rushee2 whose ranks are Rushee1 and Rushee2
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
        if row['OR'] == Rushee2:
            r2_idx = index
            
    #ERROR CHECKING
    if (df.iloc[r1_idx]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[r1_idx]['Full Name']} is locked")
        return False
    if (df.iloc[r2_idx]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[r2_idx]['Full Name']} is locked")
        return False
    #swap the ranks of rushee1 and rushee2
    row1, row2 = df.iloc[r1_idx], df.iloc[r2_idx]
    temp = row1.copy()
    df.iloc[r1_idx] = row2
    df.iloc[r2_idx] = temp
    return True
    
def drop(Rushee1, location):
    global df
    # create an empty dataframe with the same columns as df
    temp_df = pd.DataFrame(columns=df.columns)
    # add len(df) blank rows to temp_df
    temp_df = pd.concat([temp_df, pd.DataFrame([{} for i in range(len(df))])], ignore_index=True)
    r1_idx = -1
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
    
    temp_df_indices = [i for i in range(len(df))]
    df_indices = [i for i in range(len(df))]
    dropping_to = location - 1

    #ERROR CHECKING
    if (dropping_to <= r1_idx):
        print(f"Cannot drop rushee to a higher rank than their current rank")
        return False
    if (df.iloc[dropping_to]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[location]['Full Name']} is locked")
        return False
    if (df.iloc[r1_idx]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[r1_idx]['Full Name']} is locked")
        return False
    #everybody below rushee
    for idx in range(location, len(df)):
        if idx in temp_df_indices:
            temp_df.iloc[idx] = df.iloc[idx]
            temp_df_indices.remove(idx)
            df_indices.remove(idx)

    # rushee
    temp_df.iloc[dropping_to] = df.iloc[r1_idx]
    temp_df_indices.remove(dropping_to)
    df_indices.remove(r1_idx)
        
    #everybody locked 
    for idx in range(len(df)):
        if (df.iloc[idx]['Strikes']["val"] == 2):
            if idx in temp_df_indices:
                temp_df.iloc[idx] = df.iloc[idx]
                temp_df_indices.remove(idx)
                df_indices.remove(idx)
    
    #everbody else
    for temp_idx, df_idx in zip(temp_df_indices, df_indices):
        temp_df.iloc[temp_idx] = df.iloc[df_idx]
    
    df = temp_df
    return True

def jump(Rushee1, location):
    global df
    # create an empty dataframe with the same columns as df
    temp_df = pd.DataFrame(columns=df.columns)
    # add len(df) blank rows to temp_df
    temp_df = pd.concat([temp_df, pd.DataFrame([{} for i in range(len(df))])], ignore_index=True)
    r1_idx = -1
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
    
    temp_df_indices = [i for i in range(len(df))]
    df_indices = [i for i in range(len(df))]

    jumping_to = location - 1
    
    #ERROR CHECKING
    if (jumping_to >= r1_idx):
        print(f"Cannot jump rushee to a lower rank than their current rank")
        return False
    if (df.iloc[jumping_to]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[location]['Full Name']} is locked")
        return False
    if (df.iloc[r1_idx]['Strikes']["val"] >= 2):
        print(f"Rushee {df.iloc[r1_idx]['Full Name']} is locked")
        return False
    #everybody above location
    for idx in range(0, jumping_to):
        temp_df.iloc[idx] = df.iloc[idx]
        temp_df_indices.remove(idx)
        df_indices.remove(idx)
    
    #rushee
    temp_df.iloc[jumping_to] = df.iloc[r1_idx]
    temp_df_indices.remove(jumping_to)
    df_indices.remove(r1_idx)
        
    #everybody locked 
    for idx in range(len(df)):
        if (df.iloc[idx]['Strikes']["val"] == 2):
            if idx in temp_df_indices:
                temp_df.iloc[idx] = df.iloc[idx]
                temp_df_indices.remove(idx)
                df_indices.remove(idx)
    
    #everbody else
    for temp_idx, df_idx in zip(temp_df_indices, df_indices):
        temp_df.iloc[temp_idx] = df.iloc[df_idx]
    
    df = temp_df 
    return True  


def strike(Rushee1):
    global df
    r1_idx = -1
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
    df.at[r1_idx, 'Strikes']["val"] += 1

def lock_rushee(Rushee1):
    global df
    r1_idx = -1
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
    df.at[r1_idx, 'Strikes']["val"] =2

def lock_range(Rushee1, Rushee2):
    global df
    r1_idx = -1
    r2_idx = -1
    for index, row in df.iterrows():
        if row['OR'] == Rushee1:
            r1_idx = index
        if row['OR'] == Rushee2:
            r2_idx = index
    for i in range(r1_idx, r2_idx+1):
        df.at[i, 'Strikes']["val"] =2
    
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
    global genuine
    global glue
    global benefit
    global mid
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
            df.drop(df.columns[0:3], axis=1, inplace=True)
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
                if swap(int(request.form["rushee1"]), int(request.form["optional"])):
                    strike(int(request.form["rushee1"]))
                    strike(int(request.form["optional"]))
            if request.form["motion"] == "drop":
                if drop(int(request.form["rushee1"]), int(request.form["optional"])):
                    strike(int(request.form["rushee1"]))
            if request.form["motion"] == "jump":
                if jump(int(request.form["rushee1"]), int(request.form["optional"])):
                    strike(int(request.form["rushee1"]))
            if request.form["motion"] == "strike":
                strike(int(request.form["rushee1"]))
            if request.form["motion"] == "lock" and request.form["optional"] == "":
                lock_rushee(int(request.form["rushee1"]))
            if request.form["motion"] == "lock" and request.form["optional"] != "":
                lock_range(int(request.form["rushee1"]), int(request.form["optional"]))
            if request.form["motion"] == "save":
                # store columns 0 and 1 and the last column in a dataframe
                middle_val = df.iloc[:, 0:3]
                # drop columns 1 and 2
                df.drop(df.columns[0:3], axis=1, inplace=True)
                for idx, name in enumerate(df):
                    col_name = name
                    # each val in name.value calcaulte its percentil
                    col_val_with_color = []
                    for val in df[name]:
                        col_val_with_color.append(val["val"])
                
                    # drop the column and add it again in the same position
                    df.drop(col_name, axis=1, inplace=True)
                    df.insert(idx, col_name, col_val_with_color)
                df = pd.concat([middle_val, df], axis=1)
                save()

                # store columns 0 and 1 and the last column in a dataframe
                middle = df.iloc[:, 0:3]
                df.drop(df.columns[0:3], axis=1, inplace=True)
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

            if request.form["motion"] == "genuine":
                genuine += 1
            
            if request.form["motion"] == "glue":
                glue += 1
            
            if request.form["motion"] == "would":
                benefit += 1

            if request.form["motion"] == "mid":
                mid += 1
            middle = int(len(df.values) / 2)
            rushees_top = df.iloc[:middle]
            rushees_bottom = df.iloc[middle:]
            return render_template("vm2.html", rows=row, rushees1=rushees_top, rushees2=rushees_bottom, middle=middle, remove= -1 * remove)


if __name__ == '__main__':
    app.run(debug=True)