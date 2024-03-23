import pandas as pd
import matplotlib.pyplot as pyplot
from sklearn.impute import SimpleImputer
import numpy as np

#method used to imputate only numeric empty values
def inputate_numeric_values(data): 
    categorical_columns = []
    numeric_columns = []
    for c in data.columns:
      if data[c].map(type).eq(str).any(): #check if there are any strings in column
        categorical_columns.append(c)
      else:
        numeric_columns.append(c)

    #create two DataFrames, one for each data type
    data_numeric = data[numeric_columns]
    data_categorical = pd.DataFrame(data[categorical_columns])
    
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    data_numeric = pd.DataFrame(imp.fit_transform(data_numeric), columns = data_numeric.columns, index=data_numeric.index) #only apply imputer to numeric columns

    #join the two masked dataframes back together
    return pd.concat([data_numeric, data_categorical], axis = 1)

#1. read csv and add team_name column
players = pd.read_csv("data/players.csv").rename(columns={'id': 'player_id','current_team_id':'team_id'})
player_data = pd.read_csv("data/player_data_per_36_min.csv")
teams = pd.read_csv("data/teams.csv")

merged_player_data = pd.merge(players,player_data,on='player_id')
player_data_with_team_name = pd.merge(merged_player_data,teams[['team_id','team_name']],on='team_id', how='left')

#2. imputate data and filter out players without a team
imputated_player_data = inputate_numeric_values(player_data_with_team_name)
filtered_data = imputated_player_data.dropna(subset=["team_name"])

#3. group by player id and team name
data_grouped_by_player = filtered_data.groupby(['player_id'])
data_grouped_by_team = filtered_data.groupby(['team_name'])

#5 save tables to csv
def compression_options(name): 
    return dict(method='zip',archive_name=name)

data_grouped_by_player.to_csv('playerData.zip', index=False, compression=compression_options('playerData.zip'))   
data_grouped_by_team.to_csv('teamData.zip', index=False, compression=compression_options('teamData.zip'))  
