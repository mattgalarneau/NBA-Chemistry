# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 19:43:25 2019

@author: Matthew
"""

import os
os.chdir("C:/Users/Matthew/Desktop/NBA_Model/")
import sys
path = os.getcwd()+'\\Code\\Class'
if path not in sys.path: 
    sys.path.append(path)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from Team import Team

from tqdm import tqdm

conn1 = sqlite3.connect("DB/Game_Info.sqlite")
homeaway = pd.read_sql("select * from HomeAway", conn1)
homeaway['GAME_DATE'] = pd.to_datetime(homeaway['GAME_DATE'])
conn1.close()

games = homeaway[(homeaway['SEASON_YEAR'] == '2018-19') & (homeaway['SEASON_TYPE'] == 'Regular Season')]

all_teams_all_dates = {}

teams = games['HOME_TEAM_ID'].unique()

for team in tqdm(teams):

    team_ = Team(team)
    
    team_games = games[(games['HOME_TEAM_ID'] == team) | (games['AWAY_TEAM_ID'] == team)]
    game_dates = team_games['GAME_DATE'].dt.date
    
    team_df = pd.DataFrame(index=game_dates, columns=['DEFLECTIONS', 'CONTESTED_SHOTS', 'SCREEN_ASSISTS', 'SECONDARY_AST'], dtype=np.float64)

    for game_date in game_dates:
        hustle = team_.hustle(per48=False,season='2018-19',as_of_date=game_date,columns=['DEFLECTIONS', 'CONTESTED_SHOTS', 'SCREEN_ASSISTS'], last_n_games=1)
        tracking = team_.tracking(per48=False,season='2018-19',as_of_date=game_date, columns=['SECONDARY_AST'], last_n_games=1)
        
        comb = hustle.append(tracking)
        
        team_df.loc[game_date] = comb
        
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0,100))
    
    team_df = team_df.dropna()
    team_df_scaled = pd.DataFrame(scaler.fit_transform(team_df), columns=team_df.columns, index=pd.to_datetime(team_df.index))
    chemistry = team_df_scaled.mean(axis=1)
    chemistry = chemistry.rolling(window=8).mean()
    chemistry = 100 * chemistry / chemistry.dropna().iloc[0]
    
    
    all_teams_all_dates[team] = chemistry
    

os.chdir("C:/Users/Matthew/Desktop/NBA Chemistry/")
mapping = pd.read_csv('Mapping.csv', index_col=0)

for team_id in mapping.index:
    df = all_teams_all_dates[team_id]
    info = mapping.loc[team_id]
    abbv = info['TeamAbbv']
    dates = info[info.index.str.contains('Date')].dropna().values
    descriptions = info[info.index.str.contains('Description')].dropna().values
    fig, ax = plt.subplots()
    ax.plot_date(df.index, df.values, '-')  
    for date, description in zip(dates, descriptions):
        ax.plot_date(pd.to_datetime(date), df.loc[pd.to_datetime(date)], 'o', label=description)
    if len(dates) > 0:
        ax.legend(loc=2, prop={'size':10})
    plt.title(abbv, fontsize=24)
    plt.savefig('Plots/'+abbv+'.png')
