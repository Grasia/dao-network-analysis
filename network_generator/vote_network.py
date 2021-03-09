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
from typing import List, Dict, Tuple, Set


def filter_votes_by_proposal_outcome(proposal: str, outcome: str, votes: pd.DataFrame) -> pd.DataFrame:
    v_filter: pd.DataFrame = votes
    v_filter = v_filter[v_filter['proposal'] == proposal]
    v_filter = v_filter[v_filter['outcome'] == outcome]
    return v_filter


def make_edges(votes: pd.DataFrame, hash_index: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    edges: Dict[str, Tuple[str, str]] = dict()

    for i in range(len(votes)):
        for j in range(i+1, len(votes)):
            e_to   = votes.iloc[i]['voter']
            e_from = votes.iloc[j]['voter']

            # check if voters are also reputation holders
            if e_to not in hash_index.keys():
                continue
            if e_from not in hash_index.keys():
                continue

            e_to   = hash_index[e_to]
            e_from = hash_index[e_from]
            
            edges[f'{e_to}{e_from}'] = (e_to, e_from)

    return edges


def get_edges_as_list(votes: pd.DataFrame, hash_index: Dict[str, int]) -> List[Tuple[int, int, int]]:
    proposals: Set[str] = set(votes['proposal'].tolist())
    edges_list: List[Dict] = []
    weight_edges: Dict = dict() # key: list[to, from, weight]

    # calculate by vote all the edges with weight 1
    for p in proposals:
        pass_votes: pd.DataFrame = filter_votes_by_proposal_outcome(proposal=p, outcome='Pass', votes=votes)
        fail_votes: pd.DataFrame = filter_votes_by_proposal_outcome(proposal=p, outcome='Fail', votes=votes)

        edges_list.append(make_edges(votes=pass_votes, hash_index=hash_index))
        edges_list.append(make_edges(votes=fail_votes, hash_index=hash_index))

    # join all commmon edges increasing weight
    for edges in edges_list:
        for edge in edges.keys():
            e_to: int   = edges[edge][0]
            e_from: int = edges[edge][1]

            if edge in weight_edges:
                weight: int = weight_edges[edge][2]
                weight_edges[edge] = (e_to, e_from, weight+1)
            elif f'{e_from}{e_to}' in weight_edges:
                k: str = f'{e_from}{e_to}'
                weight: int = weight_edges[k][2]
                weight_edges[k] = (e_from, e_to, weight+1)
            else:
                weight_edges[edge] = (e_to, e_from, 1)

    return [v for k, v in weight_edges.items()]


def get_nodes_and_map(users: pd.DataFrame) -> Tuple[List[Tuple[str, Dict]], Dict[str, int]]:
    nodes: List = []
    index: int = 0
    hash_index: Dict[str, int] = {}

    # order by address in order to get always the same index
    users = users.sort_values(by=['address'])

    for i, row in users.iterrows():
        nodes.append(
            (index, {'hash': row['address'], 'reputation': row['balance']})
        )
        hash_index[row['address']] = index
        index += 1

    return (nodes, hash_index)


def make_graph(users: pd.DataFrame, votes: pd.DataFrame) -> nx.Graph:
    graph: nx.Graph = nx.Graph()

    nodes, hash_index = get_nodes_and_map(users=users)
    graph.add_nodes_from(nodes_for_adding=nodes)

    graph.add_weighted_edges_from(ebunch_to_add=get_edges_as_list(votes=votes, hash_index=hash_index))
    return graph


def parse_reputation(df: pd.DataFrame) -> pd.DataFrame:
    dff: pd.DataFrame = df
    balances = []
    min_b: int = sys.maxsize
    max_b: int = -1

    for i, row in dff.iterrows():
        b = int(row['balance'])
        balances.append(b)

        if b < min_b:
            min_b = b
        if b > max_b:
            max_b = b

    # normalize data between [0, 100]
    divider = max_b - min_b
    for i in range(len(balances)):
        balances[i] = (balances[i] - min_b) / divider * 100

    dff.pop('balance')
    dff['balance'] = balances
    dff = dff.sort_values(by=['balance'], ascending=False)

    return dff


if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg
    if len(sys.argv) != 2:
        print('ERROR: python vote_network.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]
    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users = parse_reputation(df=users)
    users.reset_index(inplace=True)

    votes: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'votes.csv'), header=0)
    votes = votes[votes['dao'] == dao_id]
    votes.reset_index(inplace=True)

    nx.write_gml(make_graph(users=users, votes=votes), os.path.join('data', 'network', f'{sys.argv[1]}_vote.gml'))
