# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 21:54:04 2019

@author: Matthew
"""

import os
import sys
path = os.getcwd()+'\\Code\\Class'
if path not in sys.path: 
    sys.path.append(path)

import pandas as pd
import sqlite3
from League import League

from tqdm import tqdm

conn1 = sqlite3.connect("DB/Game_Info.sqlite")
homeaway = pd.read_sql("select * from HomeAway", conn1)
homeaway['GAME_DATE'] = pd.to_datetime(homeaway['GAME_DATE'])
conn1.close()

seasons = homeaway[(homeaway['SEASON_YEAR'] >= '2016-17') & (homeaway['SEASON_YEAR'] <= '2018-19') & (homeaway['SEASON_TYPE'] == 'Regular Season')]
dates = seasons['GAME_DATE'].dt.date.unique()

all_teams_all_dates = pd.DataFrame()

for date in tqdm(dates):

    league = League(date)
    
    hustle = league.hustle(columns=['CHARGES_DRAWN', 'DEFLECTIONS', 'CONTESTED_SHOTS', 'SCREEN_ASSISTS'])
    tracking = league.tracking(columns=['SECONDARY_AST', 'PASSES_MADE', 'POTENTIAL_AST'])
    tracking['PASSES_TO_AST'] = tracking['PASSES_MADE'] / tracking['POTENTIAL_AST']
    tracking = tracking.drop(['PASSES_MADE', 'POTENTIAL_AST'], axis=1)
    pace = league.advanced(columns=['PACE'])
    
    comb = hustle.join(tracking)
    
    comb = comb.multiply(pace.PACE / 100, axis=0)
    
    from sklearn.preprocessing import MinMaxScaler
    
    scaler = MinMaxScaler(feature_range=(0,100))
    
    comb_scaled = pd.DataFrame(scaler.fit_transform(comb), columns=comb.columns, index=comb.index)
    
    if comb_scaled.shape[0] == 30:
        all_teams_all_dates[date] = comb_scaled.mean(axis=1)