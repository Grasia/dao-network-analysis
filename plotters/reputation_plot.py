"""
   Descp: Plots reputation distribution of a DAO as parameter.

   Created on: 23-feb-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import os
import sys
import pandas as pd
import plotly.graph_objects as go
from utils.time_filter import filter_date


def plot(df: pd.DataFrame) -> None:
    fig = go.Figure()

    # mean reputation
    rep_mean: float = sum(df['balance'].tolist()) / len(df)
    fig.add_hline(y=rep_mean, line_dash="dashdot", opacity=1)

    # 50% reputation
    rep_50 = sum(df['balance'].tolist()) / 2.0
    half = 0
    added = False
    for i, b in enumerate(df['balance'].tolist()):
        if not added and (half > rep_50):
            fig.add_vline(x=f'{i}', opacity=1, line_dash="dashdot")
            added = True
    
        half += b

        fig.add_trace(
            go.Bar(x=[f'{i}'], y=[b])
        )

    # Add figure title
    fig.update_layout(
        # legend={
        #     'orientation': 'v', 
        #     'x': 1, 
        #     'y': 0.5,
        #     'font': {'size': 44},
        #     'bordercolor': "Black",
        #     'borderwidth': 2,
        #     'itemsizing': 'constant'},
        xaxis={
            'ticks': 'outside',
            'ticklen': 5,
            'tickwidth': 2,
            'showline': True, 
            'linewidth': 2,
            'linecolor': 'black',
            'showgrid': True,
            'gridwidth': 0.5,
            'gridcolor': '#B0BEC5',
            'tickfont': {'size': 20},
        },
        yaxis={
            'showgrid': True,
            'gridwidth': 0.5,
            'gridcolor': '#B0BEC5',
            'ticks': 'outside',
            'ticklen': 5,
            'tickwidth': 2,
            'showline': True, 
            'linewidth': 2, 
            'linecolor': 'black',
            'tickfont': {'size': 20},
        },
        #title=plot_title,
        plot_bgcolor="white",
        barmode='group',
        showlegend=False,
    )
    fig.update_xaxes(
        title_text = "Reputation Holder Index",
        title_font = {"size": 20},
        title_standoff = 25)

    fig.update_yaxes(
        title_text = "Reputation amount",
        title_font = {"size": 20},
        title_standoff = 25)

    fig.show()


if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg, Genesis Alpha
    if len(sys.argv) != 2:
        print('ERROR: python reputation_plot.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]
    df: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    df = df[df['dao'] == dao_id]
    df = filter_date(df=df, date_key='createdAt', date='01/04/2021')
    
    balances = []
    for i, row in df.iterrows():
        balances.append(int(row['balance']))

    df.pop('balance')
    df['balance'] = balances
    df = df.sort_values(by=['balance'], ascending=False)

    plot(df=df)
