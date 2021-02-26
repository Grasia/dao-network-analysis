"""
   Descp: Generates a complex network of the voting system of a DAO set as parameter. 

   Created on: 26-feb-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import pandas as pd
import networkx as nx
import os
import sys
from typing import List, Dict, Tuple


def get_edges_as_list(votes: pd.DataFrame) -> List[Tuple[str, str, int]]:
    pass


def get_nodes_as_list(users: pd.DataFrame) -> List[Tuple(str, Dict[str, int])]:
    nodes: List = []
    for i, row in users.iterrows():
        nodes.append(
            (row['id'], {'reputation': row['balance']})
        )
    return nodes


def make_graph(users: pd.DataFrame, votes: pd.DataFrame) -> nx.Graph:
    graph: nx.Graph = nx.Graph()
    graph.add_nodes_from(nodes_for_adding=get_nodes_as_list(users=users))
    graph.add_weighted_edges_from(ebunch_to_add=)
    return graph


def parse_reputation(df: pd.DataFrame) -> pd.DataFrame:
    dff: pd.DataFrame = df
    balances = []

    for i, row in dff.iterrows():
        balances.append(int(row['balance']))

    dff.pop('balance')
    dff['balance'] = balances
    dff = dff.sort_values(by=['balance'], ascending=False)

    return dff


if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg
    if len(sys.argv) != 2:
        print('ERROR: python reputation_plot.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]
    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users = parse_reputation(df=users)

