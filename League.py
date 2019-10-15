# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 00:19:36 2019

@author: galar
"""

import pandas as pd
import sqlite3

# Faster to read in all of the sql tables rather than each time an instance is created
conn1 = sqlite3.connect("DB/NBA_Stats.sqlite")
stats_df = pd.read_sql("select * from Stats", conn1)
stats_df.GAME_DATE = pd.to_datetime(stats_df.GAME_DATE)
stats_df = stats_df[['GAME_DATE','SEASON_YEAR', 'SEASON_TYPE']]
stats_df = stats_df.drop_duplicates()
stats_df = stats_df.set_index('GAME_DATE').sort_index()
stats_df = stats_df.resample('D').ffill()
hustle_df = pd.read_sql("select * from Hustle", conn1)
hustle_df.Date = pd.to_datetime(hustle_df.Date).dt.date
hustle_df = hustle_df.set_index(['Date', 'TEAM_ID', 'TEAM_NAME'])
general_df = pd.read_sql("select * from General", conn1)
general_df.Date = pd.to_datetime(general_df.Date).dt.date
general_df = general_df.set_index(['Date', 'TEAM_ID', 'TEAM_NAME'])
tracking_df = pd.read_sql("select * from Tracking", conn1)
tracking_df.Date = pd.to_datetime(tracking_df.Date).dt.date
tracking_df = tracking_df.set_index(['Date', 'TEAM_ID', 'TEAM_NAME'])
conn1.close()

class League:
    '''
    League class is a snapshot of league averages on a given day    
    '''
    def __init__(self,date):
        '''
        An instance will be required to have a given date
        Typically the day before a game you are trying to evaluate
        On that day, we are in a certain season, and that date either it is Regular Season or Playoffs
        '''
        self.date = date
        self.season_year = stats_df.loc[self.date].SEASON_YEAR
        self.season_type = stats_df.loc[self.date].SEASON_TYPE
    
    def general(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True)  
        Output:
            league average of selected stats as of self.date
        '''
        league_df = general_df.copy()
        
        league_df = league_df[(league_df['SEASON_YEAR'] == self.season_year) & (league_df['SEASON_TYPE'] == self.season_type)]

        league_df = league_df.drop(['CFPARAMS', 'CFID', 'SEASON_YEAR', 'SEASON_TYPE'], axis=1)
        
        # these columns must be calculated at the end (see below)
        filtered_columns = ['W_PCT', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'OPP_FG_PCT', 'OPP_FG3_PCT', 'OPP_FT_PCT']
        league_df_filtered = league_df.drop(filtered_columns, axis=1)
        
        grouped = league_df_filtered.groupby(level=1)
        
        league_df_filtered = grouped.diff().fillna(grouped.cumsum())
        
        league_df_filtered = league_df_filtered[league_df_filtered['MIN'] > 0]
                
        if start_date:
            league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date >= start_date]
        
        league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date <= self.date]
        
        league_df_filtered = league_df_filtered.groupby(level=1).mean()
        
        if per48:
            league_df_filtered = league_df_filtered.div(league_df_filtered.MIN, axis='rows') * 48
                
        league_df_filtered['FG_PCT'] = league_df_filtered['FGM'] / league_df_filtered['FGA']
        league_df_filtered['FG3_PCT'] = league_df_filtered['FG3M'] / league_df_filtered['FG3A']
        league_df_filtered['FT_PCT'] = league_df_filtered['FTM'] / league_df_filtered['FTA']
        league_df_filtered['OPP_FG_PCT'] = league_df_filtered['OPP_FGM'] / league_df_filtered['OPP_FGA']
        league_df_filtered['OPP_FG3_PCT'] = league_df_filtered['OPP_FG3M'] / league_df_filtered['OPP_FG3A']
        league_df_filtered['OPP_FT_PCT'] = league_df_filtered['OPP_FTM'] / league_df_filtered['OPP_FTA']
        
        if columns is not None:
            return league_df_filtered[columns]
        else:
            return league_df_filtered
    
    def hustle(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True)
        Output:
            league average of selected stats as of self.date
        '''
        league_df = hustle_df.copy()
        
        league_df = league_df[(league_df['SEASON_YEAR'] == self.season_year) & (league_df['SEASON_TYPE'] == self.season_type)]

        league_df = league_df.drop(['SEASON_YEAR', 'SEASON_TYPE'], axis=1)
                
        # these columns must be calculated at the end (see below)
        filtered_columns = ['PCT_BOX_OUTS_DEF', 'PCT_BOX_OUTS_OFF', 'PCT_LOOSE_BALLS_RECOVERED_DEF', 'PCT_LOOSE_BALLS_RECOVERED_OFF']
        league_df_filtered = league_df.drop(filtered_columns, axis=1)
        
        grouped = league_df_filtered.groupby(level=1)
        
        league_df_filtered = grouped.diff().fillna(grouped.cumsum())
        
        league_df_filtered = league_df_filtered[league_df_filtered['MIN'] > 0]
                
        if start_date:
            league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date >= start_date]
        
        league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date <= self.date]
        
        league_df_filtered = league_df_filtered.groupby(level=1).mean() 
        
        if per48:
            league_df_filtered = league_df_filtered.div(league_df_filtered.MIN, axis='rows') * 48
        
        league_df_filtered['PCT_BOX_OUTS_DEF'] = league_df_filtered['DEF_BOXOUTS'] / league_df_filtered['BOX_OUTS']
        league_df_filtered['PCT_BOX_OUTS_OFF'] = league_df_filtered['OFF_BOXOUTS'] / league_df_filtered['BOX_OUTS']
        league_df_filtered['PCT_LOOSE_BALLS_RECOVERED_DEF'] = league_df_filtered['DEF_LOOSE_BALLS_RECOVERED'] / league_df_filtered['LOOSE_BALLS_RECOVERED']
        league_df_filtered['PCT_LOOSE_BALLS_RECOVERED_OFF'] = league_df_filtered['OFF_LOOSE_BALLS_RECOVERED'] / league_df_filtered['LOOSE_BALLS_RECOVERED']

        if columns is not None:
            return league_df_filtered[columns]
        else:
            return league_df_filtered
        
    def tracking(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True) 
        Output:
            league average of selected stats as of self.date
        '''
        league_df = tracking_df.copy()
        league_general_df = self.general(start_date=start_date, per48=per48)
        
        league_df = league_df[(league_df['SEASON_YEAR'] == self.season_year) & (league_df['SEASON_TYPE'] == self.season_type)]
        
        league_df = league_df.drop(['TEAM_ABBREVIATION','SEASON_YEAR', 'SEASON_TYPE'], axis=1)
               
        # these columns must be calculated at the end (see below)
        filtered_columns = ['AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ', 'AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH',
                            'PTS_PER_TOUCH', 'PTS_PER_ELBOW_TOUCH', 'PTS_PER_POST_TOUCH', 'PTS_PER_PAINT_TOUCH',
                            'OREB_CONTEST_PCT', 'OREB_CHANCE_PCT', 'OREB_CHANCE_PCT_ADJ', 'AVG_OREB_DIST',
                            'DREB_CONTEST_PCT', 'DREB_CHANCE_PCT', 'DREB_CHANCE_PCT_ADJ', 'AVG_DREB_DIST',
                            'REB_CONTEST_PCT', 'REB_CHANCE_PCT', 'REB_CHANCE_PCT_ADJ', 'AVG_REB_DIST', 'EFF_FG_PCT',
                            'DRIVE_FG_PCT', 'CATCH_SHOOT_FG_PCT', 'PULL_UP_FG_PCT', 'PAINT_TOUCH_FG_PCT',
                            'POST_TOUCH_FG_PCT', 'ELBOW_TOUCH_FG_PCT', 'AVG_SPEED', 'AVG_SPEED_OFF', 'AVG_SPEED_DEF']

        league_df_filtered = league_df.drop(filtered_columns, axis=1)
        
        grouped = league_df_filtered.groupby(level=1)
        
        league_df_filtered = grouped.diff().fillna(grouped.cumsum())
        
        league_df_filtered = league_df_filtered[league_df_filtered['MIN'] > 0]
                
        if start_date:
            league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date >= start_date]
        
        league_df_filtered = league_df_filtered[league_df_filtered.index.get_level_values('Date').date <= self.date]
        
        league_df_filtered = league_df_filtered.groupby(level=1).mean()        
        
        if per48:
            league_df_filtered = league_df_filtered.div(league_df_filtered.MIN, axis='rows') * 240
        
        league_df = league_df.reset_index().set_index(['TEAM_ID', 'Date'])
        league_df = league_df[league_df.index.get_level_values('Date').date <= self.date]
        league_df = league_df.xs(league_df.index.get_level_values('Date')[-1], level='Date')
        
        league_df_filtered['AST_TO_PASS_PCT'] = (league_df_filtered['AST_ADJ'] - league_df_filtered['SECONDARY_AST'] - league_df_filtered['FT_AST']) / league_df_filtered['PASSES_MADE']
        league_df_filtered['AST_TO_PASS_PCT_ADJ'] = league_df_filtered['AST_ADJ'] / league_df_filtered['PASSES_MADE']
        league_df_filtered['AVG_SEC_PER_TOUCH'] = (league_df_filtered['TIME_OF_POSS'] * 60) / league_df_filtered['TOUCHES']
        league_df_filtered['PTS_PER_TOUCH'] = league_general_df['PTS'] / league_df_filtered['TOUCHES']
        league_df_filtered['PTS_PER_ELBOW_TOUCH'] = league_df_filtered['ELBOW_TOUCH_PTS'] / league_df_filtered['ELBOW_TOUCHES']
        league_df_filtered['PTS_PER_POST_TOUCH'] = league_df_filtered['POST_TOUCH_PTS'] / league_df_filtered['POST_TOUCHES']
        league_df_filtered['PTS_PER_PAINT_TOUCH'] = league_df_filtered['PAINT_TOUCH_PTS'] / league_df_filtered['PAINT_TOUCHES']
        league_df_filtered['OREB_CONTEST_PCT'] = league_df_filtered['OREB_CONTEST'] / league_df_filtered['OREB']
        league_df_filtered['OREB_CHANCE_PCT'] = league_df_filtered['OREB'] / league_df_filtered['OREB_CHANCES']
        league_df_filtered['OREB_CHANCE_PCT_ADJ'] = league_df_filtered['OREB'] / (league_df_filtered['DREB_CHANCES'] - league_df_filtered['OREB_CHANCE_DEFER'])
        league_df_filtered['DREB_CONTEST_PCT'] = league_df_filtered['DREB_CONTEST'] / league_df_filtered['DREB']
        league_df_filtered['DREB_CHANCE_PCT'] = league_df_filtered['DREB'] / league_df_filtered['DREB_CHANCES']
        league_df_filtered['DREB_CHANCE_PCT_ADJ'] = league_df_filtered['DREB'] / (league_df_filtered['DREB_CHANCES'] - league_df_filtered['DREB_CHANCE_DEFER'])
        league_df_filtered['REB_CONTEST_PCT'] = league_df_filtered['REB_CONTEST'] / (league_df_filtered['OREB'] + league_df_filtered['DREB'])
        league_df_filtered['REB_CHANCE_PCT'] = (league_df_filtered['OREB'] + league_df_filtered['DREB'])/ league_df_filtered['REB_CHANCES']
        league_df_filtered['REB_CHANCE_PCT_ADJ'] = (league_df_filtered['OREB'] + league_df_filtered['DREB']) / (league_df_filtered['REB_CHANCES'] - league_df_filtered['REB_CHANCE_DEFER'])
        
        league_df_filtered['AVG_DRIB_PER_TOUCH'] = league_df['AVG_DRIB_PER_TOUCH']
        league_df_filtered['AVG_OREB_DIST'] = league_df['AVG_OREB_DIST']
        league_df_filtered['AVG_DREB_DIST'] = league_df['AVG_DREB_DIST']
        league_df_filtered['AVG_REB_DIST'] = league_df['AVG_REB_DIST']
        league_df_filtered['DRIVE_FG_PCT'] = league_df['DRIVE_FG_PCT']
        league_df_filtered['CATCH_SHOOT_FG_PCT'] = league_df['CATCH_SHOOT_FG_PCT']
        league_df_filtered['PULL_UP_FG_PCT'] = league_df['PULL_UP_FG_PCT']
        league_df_filtered['PAINT_TOUCH_FG_PCT'] = league_df['PAINT_TOUCH_FG_PCT']
        league_df_filtered['POST_TOUCH_FG_PCT'] = league_df['POST_TOUCH_FG_PCT']
        league_df_filtered['ELBOW_TOUCH_FG_PCT'] = league_df['ELBOW_TOUCH_FG_PCT']
        league_df_filtered['AVG_SPEED'] = league_df['AVG_SPEED']
        league_df_filtered['AVG_SPEED_OFF'] = league_df['AVG_SPEED_OFF']
        league_df_filtered['AVG_SPEED_DEF'] = league_df['AVG_SPEED_DEF']
        
        if columns is not None:
            return league_df_filtered[columns]
        else:
            return league_df_filtered
    
    def advanced(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True)
        Output:
            league average of selected stats as of self.date
        '''
        
        # all advanced stats are based off of general stats
        league_df = self.general(start_date=start_date, per48=per48)
        
        adv_df = pd.DataFrame(index=league_df.index)
        
        # more accurate way??
        POSS = 0.5*((league_df.FGA+0.4*league_df.FTA-1.07*(league_df.OREB/(league_df.OREB+league_df.OPP_DREB))*(league_df.FGA-league_df.FGM)+league_df.TOV)+(league_df.OPP_FGA+0.4*league_df.OPP_FTA-1.07*(league_df.OPP_OREB/(league_df.OPP_OREB+league_df.DREB))*(league_df.OPP_FGA-league_df.OPP_FGM)+league_df.OPP_TOV))
       
        adv_df['OFF_RTG'] = 100 * (league_df.PTS/POSS)
        adv_df['DEF_RTG'] = 100 * (league_df.OPP_PTS/POSS)
        adv_df['NET_RTG'] = adv_df['OFF_RTG'] - adv_df['DEF_RTG']
        adv_df['AST_PCT'] = league_df.AST / (league_df.FGM)
        adv_df['AST_TO'] = league_df.AST / league_df.TOV
        adv_df['AST_RATIO'] = (league_df.AST * 100) / POSS
        adv_df['OREB_PCT'] = league_df.OREB / (league_df.OREB + league_df.OPP_DREB)
        adv_df['DREB_PCT'] = league_df.DREB / (league_df.OPP_OREB + league_df.DREB)
        adv_df['REB_PCT'] = league_df.REB / (league_df.REB + league_df.OPP_REB)
        adv_df['TOV_PCT'] = league_df.TOV / (league_df.FGA + 0.44 * league_df.FTA + league_df.TOV)
        adv_df['EFG_PCT'] = (league_df.FGM + 0.5 * league_df.FG3M) / league_df.FGA
        adv_df['TS_PCT'] = league_df.PTS / (2 * (league_df.FGA + 0.44 * league_df.FTA))
        adv_df['PACE'] = (((240 * league_df.GP) / (league_df.MIN * 5)) * POSS) / league_df.GP
        adv_df['PIE'] = (league_df.PTS + league_df.FGM + league_df.FTM - league_df.FGA - league_df.FTA + league_df.DREB + (0.5 * league_df.OREB) + league_df.AST + league_df.STL + (0.5 * league_df.BLK) - league_df.PF - league_df.TOV) / (league_df.PTS + league_df.OPP_PTS + league_df.FGM + league_df.OPP_FGM + league_df.FTM + league_df.OPP_FTM - league_df.FGA - league_df.OPP_FGA - league_df.FTA - league_df.OPP_FTA + league_df.DREB + league_df.OPP_DREB + (0.5 * (league_df.OREB + league_df.OPP_OREB)) + league_df.AST + league_df.OPP_AST + league_df.STL + league_df.OPP_STL + (0.5 * (league_df.BLK + league_df.OPP_BLK)) - league_df.PF - league_df.OPP_PF - league_df.TOV - league_df.OPP_TOV)

        if columns is not None:
            return adv_df[columns]
        else:
            return adv_df

    def fourfactors(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True)
        Output:
            league average of selected stats as of self.date
        '''
        
        # all fourfactor stats are based off of general stats
        league_df = self.general(start_date=start_date, per48=True)
        
        ff_df = pd.DataFrame(index=league_df.index)
        
        ff_df['EFG_PCT'] = (league_df.FGM + 0.5 * league_df.FG3M) / league_df.FGA
        ff_df['FTA_RATE'] = league_df.FTA / league_df.FGA
        ff_df['TOV_PCT'] = league_df.TOV / (league_df.FGA + 0.44 * league_df.FTA + league_df.TOV)
        ff_df['OREB_PCT'] = league_df.OREB / (league_df.OREB + league_df.OPP_DREB)
        ff_df['OPP_EFG_PCT'] = (league_df.OPP_FGM + 0.5 * league_df.OPP_FG3M) / league_df.OPP_FGA
        ff_df['OPP_FTA_RATE'] = league_df.OPP_FTA / league_df.OPP_FGA
        ff_df['OPP_TOV_PCT'] = league_df.OPP_TOV / (league_df.OPP_FGA + 0.44 * league_df.FTA + league_df.OPP_TOV)
        ff_df['OPP_OREB_PCT'] = league_df.OPP_OREB / (league_df.OPP_OREB + league_df.DREB)

        if columns is not None:
            return ff_df[columns]
        else:
            return ff_df
    
    def scoring(self, columns=None, start_date=None, per48=True):
        '''
        Input: 
            columns - which particular fields of general stats you want (default None returns all)
            start_date - only uses stats between start_date and self.date (default None uses entire season)
            per48 - whether or not to adjust stats per 48 minutes (default True)
        Output:
            league average of selected stats as of self.date
        '''
        
        # all scoring stats are based off of general stats
        league_df = self.general(start_date=start_date, per48=per48)
        
        scor_df = pd.DataFrame(index=league_df.index)
        
        scor_df['PCT_FGA_2P'] = (league_df.FGA - league_df.FG3A) / league_df.FGA
        scor_df['PCT_FGA_3P'] = league_df.FG3A / league_df.FGA
        scor_df['PCT_PTS_2P'] = (league_df.FGM - league_df.FG3M) * 2 / league_df.PTS
        scor_df['PCT_PTS_3P'] = league_df.FG3M * 3 / league_df.PTS
        scor_df['PCT_PTS_FB'] = league_df.PTS_FB / league_df.PTS
        scor_df['PCT_PTS_FT'] = league_df.FTM / league_df.PTS
        scor_df['PCT_PTS_OFFTO'] = league_df.PTS_OFF_TOV / league_df.PTS
        scor_df['PCT_PTS_PITP'] = league_df.PTS_PAINT / league_df.PTS
        scor_df['PCT_FG_AST'] = league_df.AST / league_df.FGM
        scor_df['PCT_FG_UAST'] = (league_df.FGM - league_df.AST) / league_df.FGM
        
        if columns is not None:
            return scor_df[columns]
        else:
            return scor_df
