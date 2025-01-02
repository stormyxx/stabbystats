from datetime import datetime, timedelta, date
import pandas as pd
import streamlit as st

class StabbyStats:

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv('Finished Games.csv')
        df['Start Date'] = pd.to_datetime(df['Start Date'], format='mixed').dt.date
        df['End Date'] = pd.to_datetime(df['End Date'], format='mixed').dt.date
        return df
    
    def render_sidebar(self):
        st.sidebar.markdown('**Useful Links**')
        st.sidebar.write('[FR Hub Thread](https://www1.flightrising.com/forums/forga/3208161)')
        st.sidebar.write('[Game History Sheet](https://docs.google.com/spreadsheets/d/15YT9N2TQ5HUJZONgnZBHJP1fYkA_8E6m8LT6kNG-bTU)')
    
    def render_body(self):
        st.title("Flight Rising IMH Game Statistics")
        self.render_overview()

    def render_overview(self):
        hcol1, hcol2 = st.columns(2)
        options = {'2w': timedelta(weeks=-2), '1mo': timedelta(days=-30), '3mo': timedelta(days=-90), '6mo': timedelta(days=-180), '1y': timedelta(days=-365), '2y': timedelta(days=-730)}
        hcol1.markdown('### Overview')
        time_range = hcol2.segmented_control("", options.keys(), default='1y')

        col1, col2, col3 = st.columns(3)
        hist_df = self.game_history[self.game_history['End Date'] < (date.today() + options.get(time_range, timedelta()))]
        hist_total = len(hist_df)
        hist_town_wins = len(hist_df[hist_df['Winning Faction'].str.contains('Town')])
        hist_maf_wins = len(hist_df[hist_df['Winning Faction'].str.contains('Mafia')])
        total_games = len(self.game_history)
        town_wins = len(self.game_history[self.game_history['Winning Faction'].str.contains('Town')])
        maf_wins = len(self.game_history[self.game_history['Winning Faction'].str.contains('Mafia')])
        col1.metric("Games Played", value=total_games, delta=f"{total_games-hist_total}")
        col2.metric('Town Win Rate', value=f"{round(town_wins*100/total_games, 2)}%", delta=f"{round((town_wins*100/total_games)-(hist_town_wins*100/hist_total), 2)}%")
        col3.metric('Mafia Win Rate', value=f"{round(maf_wins*100/total_games, 2)}%", delta=f"{round((maf_wins*100/total_games)-(hist_maf_wins*100/hist_total), 2)}%")

    def render(self):
        self.game_history = self.load_data()
        self.render_sidebar()
        self.render_body()

ss = StabbyStats()
ss.render()
