from collections import Counter
from datetime import datetime, timedelta, date
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly_calplot import calplot


class StabbyStats:

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv("Finished Games.csv")
        df["Start Date"] = pd.to_datetime(df["Start Date"], format="mixed").dt.date
        df["End Date"] = pd.to_datetime(df["End Date"], format="mixed").dt.date
        return df

    def render_sidebar(self):
        st.logo("moider.png", size="large", link="https://discord.gg/KqkMMaJBrb")
        st.sidebar.markdown("**What is this?**")
        st.sidebar.markdown("My colleague introduced me to Streamlit and I've been told that it lets me write pretty data visualisation dashboards quickly using python (my beloved programming language <3)")
        st.sidebar.markdown("The IMH game history stats are cool to look at so here's some cool IMH stat dashboard thing I made while familiarizing myself with it :D")
        st.sidebar.markdown("**Useful Links**")
        st.sidebar.write(
            "[FR Hub Thread](https://www1.flightrising.com/forums/forga/3208161)"
        )
        st.sidebar.write(
            "[Game History Sheet](https://docs.google.com/spreadsheets/d/15YT9N2TQ5HUJZONgnZBHJP1fYkA_8E6m8LT6kNG-bTU)"
        )
        st.sidebar.button(
            "click me for balloons!!!", on_click=st.balloons, type="primary"
        )

    def render_body(self):
        st.title("Flight Rising IMH Game Statistics")
        self.render_overview()
        self.render_calplot()
        self.render_winrate_trend()

    def render_overview(self):
        hcol1, hcol2 = st.columns(2)
        options = {
            "2w": timedelta(weeks=-2),
            "1mo": timedelta(days=-30),
            "3mo": timedelta(days=-90),
            "6mo": timedelta(days=-180),
            "1y": timedelta(days=-365),
            "2y": timedelta(days=-730),
        }
        hcol1.markdown("### Overview")
        time_range = hcol2.segmented_control("", options.keys(), default="1y")

        col1, col2, col3 = st.columns(3)
        hist_df = self.game_history[
            self.game_history["End Date"]
            < (date.today() + options.get(time_range, timedelta()))
        ]
        hist_total = len(hist_df)
        hist_town_wins = len(hist_df[hist_df["Winning Faction"].str.contains("Town")])
        hist_maf_wins = len(hist_df[hist_df["Winning Faction"].str.contains("Mafia")])
        total_games = len(self.game_history)
        town_wins = len(
            self.game_history[self.game_history["Winning Faction"].str.contains("Town")]
        )
        maf_wins = len(
            self.game_history[
                self.game_history["Winning Faction"].str.contains("Mafia")
            ]
        )
        col1.metric(
            "Games Played", value=total_games, delta=f"{total_games-hist_total}"
        )
        col2.metric(
            "Town Win Rate",
            value=f"{round(town_wins*100/total_games, 2)}%",
            delta=f"{round((town_wins*100/total_games)-(hist_town_wins*100/hist_total), 2)}%",
        )
        col3.metric(
            "Mafia Win Rate",
            value=f"{round(maf_wins*100/total_games, 2)}%",
            delta=f"{round((maf_wins*100/total_games)-(hist_maf_wins*100/hist_total), 2)}%",
        )

    def render_calplot(self):
        st.markdown("### Games Over Time")
        game_hist = self.game_history.to_dict("records")
        days = [
            day
            for game in game_hist
            for day in pd.date_range(
                start=game["Start Date"], end=game["End Date"], freq="D"
            )
        ]
        date_range = pd.date_range(start=min(days), end=max(days), freq="D")
        counter = Counter(days)
        calplot_df = pd.DataFrame(
            {"count": [counter[day] for day in date_range], "date": date_range}
        )
        calplot_df["date"] = calplot_df["date"].dt.date
        plt = calplot(
            calplot_df,
            x="date",
            y="count",
            name="Ongoing Games",
            month_lines=False,
            colorscale="greens",
        )
        st.plotly_chart(plt)

    def render_winrate_trend(self):
        st.markdown('### Winrate Trends')
        game_hist = self.game_history.to_dict("records")
        winrate_hist = []
        games = {"Town": 0, "Mafia": 0, "3P": 0}
        wins = {"Town": 0, "Mafia": 0, "3P": 0}

        for game in game_hist:
            for faction in ["Town", "Mafia", "3P"]:
                if faction in game["Alignments Present"]:
                    games[faction] += 1
                if faction.lower() in game["Winning Faction"].lower():
                    wins[faction] += 1
            winrate_hist.append(
                {
                    "Date": game["End Date"],
                    "Town Winrate": wins["Town"] * 100 / games["Town"],
                    "Mafia Winrate": wins["Mafia"] * 100 / games["Mafia"],
                    "3P Winrate": wins["3P"] * 100 / games["3P"],
                    "game": game["Game Name"],
                }
            )
        winrate_df = pd.DataFrame(winrate_hist)
        winrate_df = winrate_df.sort_values(by="Date")
        winrate_df = winrate_df.round(2)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=winrate_df["Date"],
                y=[0] * len(winrate_df),
                mode="lines+markers",
                name="Game",
                hovertemplate="%{text}",
                text=winrate_df["game"],
                opacity=0,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=winrate_df["Date"],
                y=winrate_df["3P Winrate"],
                mode="lines+markers",
                name="3P",
                line=dict(color="#a4a3a2"),
                hovertemplate="%{y}%"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=winrate_df["Date"],
                y=winrate_df["Town Winrate"],
                mode="lines+markers",
                name="Town",
                line=dict(color="#4dd668"),
                hovertemplate="%{y}%"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=winrate_df["Date"],
                y=winrate_df["Mafia Winrate"],
                mode="lines+markers",
                name="Mafia",
                line=dict(color="#ff5b38"),
                hovertemplate="%{y}%"
            )
        )
        fig.update_layout(hovermode="x unified", yaxis=dict(title=dict(text="Winrate (%)")))
        st.plotly_chart(fig)

    def render(self):
        self.game_history = self.load_data()
        self.render_sidebar()
        self.render_body()


ss = StabbyStats()
ss.render()
