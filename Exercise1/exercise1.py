import pandas as pd
import matplotlib.pyplot as pyplot
from sklearn.impute import SimpleImputer
import numpy as np

#import seaborn as sns

# I want to see only 2 decimals on my outcomes
pd.set_option('display.float_format', lambda x: '%.2f' % x)


# method used to imputate only numeric empty values
def imputate_numeric_values(data):
    categorical_columns = []
    numeric_columns = []
    for c in data.columns:
        if data[c].map(type).eq(str).any():  # check if there are any strings in column
            categorical_columns.append(c)
        else:
            numeric_columns.append(c)

    # create two DataFrames, one for each data type
    data_numeric = data[numeric_columns]
    data_categorical = pd.DataFrame(data[categorical_columns])

    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    data_numeric = pd.DataFrame(imp.fit_transform(data_numeric), columns=data_numeric.columns,
                                index=data_numeric.index)  # only apply imputer to numeric columns

    # join the two masked dataframes back together
    return pd.concat([data_numeric, data_categorical], axis=1)


def build_player_aggregate_dictionary(player_columns, player_data_columns):
    # creating a dictionary for use in the aggregate function of groupby

    agg_dictionary = {}
    build_player_agg(agg_dictionary, list(player_columns) + list(player_data_columns))
    return agg_dictionary


def build_player_agg(agg_dictionary, player_columns):
    sum_list = ['total_games', 'games_started', 'minutes_played']
    count_list = ['season']
    mean_list = ['fg', 'fga', 'fgp', 'fg3', 'fg3a', 'fg3p', 'fg2', 'fg2a', 'fg2p', 'ft', 'fta', 'ftp', 'orb', 'drb',
                 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']
    keep_last = ['height', 'weight', 'birth_date', 'retired', 'team_name', 'teams', 'name', 'full_name', 'position',
                 'birth_place', 'team_id', 'text', 'player_url']
    for c in list(player_columns):
        if c in sum_list:
            agg_dictionary[c] = 'sum'
        elif c in count_list:
            agg_dictionary[c] = 'count'
        elif c in mean_list:
            agg_dictionary[c] = 'mean'
        elif c in keep_last:
            agg_dictionary[c] = 'last'
        else:
            agg_dictionary[c] = 'first'
    return count_list, keep_last, mean_list, sum_list


def build_team_aggregate_dictionary(teams_columns,player_data_columns):
    # creating a dictionary for use in the aggregate function of groupby
    # first is used when we don't want to aggregate but only get the first element
    # sum is used to get the sum of the rows
    agg_dictionary = {}
    cols = list(teams_columns) + list(player_data_columns)
    mean_column_list = ['fg', 'fga', 'fgp','fg3', 'fg3a', 'fg3p', 'fg2', 'fg2a', 'fg2p', 'ft', 'fta', 'ftp', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts', 'height', 'weight']

    for c in list(cols):
        if c == 'player_id':
            agg_dictionary[c] = 'count'
        elif c in mean_column_list:
            agg_dictionary[c] = 'mean'

    # adding team_name at the end
    agg_dictionary['team_name'] = 'first'
    return agg_dictionary


# 1. read csv and add team_name column
players = pd.read_csv("data/players.csv").rename(columns={'id': 'player_id', 'current_team_id': 'team_id'})
player_data = pd.read_csv("data/player_data_per_36_min.csv")
teams = pd.read_csv("data/teams.csv")

merged_player_data = pd.merge(players, player_data, on='player_id', how='left')
player_data_with_team_name = pd.merge(merged_player_data, teams[['team_id', 'team_name']], on='team_id', how='left')

# 2. imputate data and replace team_name with 'Retired' for players without a team
imputated_player_data = imputate_numeric_values(player_data_with_team_name)
imputated_player_data.team_name = imputated_player_data.team_name.fillna("Retired")
cleaned_player_data_per_36 = imputate_numeric_values(player_data)

# 3. group by player_id and team_id
player_agg_dictionary = build_player_aggregate_dictionary(players.columns, player_data.columns)
team_agg_dictionary = build_team_aggregate_dictionary(teams.columns,player_data.columns)

data_grouped_by_player = imputated_player_data.groupby(['player_id'], as_index=False).agg(player_agg_dictionary)

# group by team_id and filter Retired players
data_grouped_by_team = imputated_player_data.groupby(['team_id'], as_index=False).agg(team_agg_dictionary)
# remove data where team is Retired , so we can group by the actual teams (obviously 'Retired' is not a team)
data_grouped_by_team = data_grouped_by_team[data_grouped_by_team.team_name != 'Retired']

#4. create scatterplot using matplotlib
minutes_played = data_grouped_by_player['minutes_played'].tolist()
fg2 = data_grouped_by_player['fg2'].tolist()
fg2a = data_grouped_by_player['fg2a'].tolist()

colors = fg2
area = fg2

pyplot.scatter(minutes_played, fg2, s=area, c=colors, alpha=0.5)
colorbar = pyplot.colorbar()
colorbar.set_label("2 Points / minutes played")
pyplot.xlabel("Minutes played")
pyplot.ylabel("2 points scored from open play")
#pyplot.show()

#create stacked for point data
teams = data_grouped_by_team['team_name'].tolist()
points = {
    "fg3p": data_grouped_by_team['fg3p'].tolist(),
    "fg2p": data_grouped_by_team['fg2p'].tolist(),
}

width = 0.2

fig, ax = pyplot.subplots()
bottom = np.zeros(len(teams))

for boolean, point in points.items():
    p = ax.bar(teams, point, width, label=boolean, bottom=bottom)
    bottom += point

ax.set_title("Points per team")
ax.legend(loc="upper right")

# Change of fontsize and angle of xticklabels
pyplot.setp(ax.get_xticklabels(), fontsize=6, rotation=80)

pyplot.show()


#5 save tables to csv
def compression_options(name):
    return dict(method='zip', archive_name=name)
#data_grouped_by_player.to_csv('playerData.zip', index=False, compression=compression_options('playerData.csv'))   
#data_grouped_by_team.to_csv('teamData.zip', index=False, compression=compression_options('teamData.csv'))
data_grouped_by_player.to_csv('playerData.csv', index=False)
data_grouped_by_team.to_csv('teamData.csv', index=False)
cleaned_player_data_per_36.to_csv('cleanedPlayerData.csv', index=False)
