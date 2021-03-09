"""
   Descp: Generates a complex network of the staking system of a DAO set as parameter. 

   Created on: 05-mar-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import pandas as pd
import networkx as nx
import os
import sys
from typing import List, Dict, Tuple, Set


def filter_stakes_by_proposal_outcome(proposal: str, outcome: str, stakes: pd.DataFrame) -> pd.DataFrame:
    v_filter: pd.DataFrame = stakes
    v_filter = v_filter[v_filter['proposal'] == proposal]
    v_filter = v_filter[v_filter['outcome'] == outcome]
    return v_filter


def make_edges(stakes: pd.DataFrame, hash_index: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    edges: Dict[str, Tuple[str, str]] = dict()

    for i in range(len(stakes)):
        for j in range(i+1, len(stakes)):
            e_to   = stakes.iloc[i]['staker']
            e_from = stakes.iloc[j]['staker']

            # check if staker are also reputation holders
            if e_to not in hash_index.keys():
                continue
            if e_from not in hash_index.keys():
                continue

            e_to   = hash_index[e_to]
            e_from = hash_index[e_from]
            
            edges[f'{e_to}{e_from}'] = (e_to, e_from)

    return edges


def get_edges_as_list(stakes: pd.DataFrame, hash_index: Dict[str, int]) -> List[Tuple[int, int, int]]:
    proposals: Set[str] = set(stakes['proposal'].tolist())
    edges_list: List[Dict] = []
    weight_edges: Dict = dict() # key: list[to, from, weight]
    counter_stakes: int = 0

    # calculate by vote all the edges with weight 1
    for p in proposals:
        pass_stakes: pd.DataFrame = filter_stakes_by_proposal_outcome(proposal=p, outcome='Pass', stakes=stakes)
        fail_stakes: pd.DataFrame = filter_stakes_by_proposal_outcome(proposal=p, outcome='Fail', stakes=stakes)

        if len(pass_stakes) > 0 and len(fail_stakes) > 0:
            counter_stakes += 1

        edges_list.append(make_edges(stakes=pass_stakes, hash_index=hash_index))
        edges_list.append(make_edges(stakes=fail_stakes, hash_index=hash_index))

    print(f'\nThere was {counter_stakes} opposite stakes in the same proposal.\n')

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


def get_nodes_and_map(users: pd.DataFrame, stakes: pd.DataFrame) -> Tuple[List[Tuple[str, Dict]], Dict[str, int]]:
    nodes: List = []
    dao_users: Set[str] = set()
    index: int = 0
    hash_index: Dict[str, int] = {}

    # order by address in order to get always the same index
    users = users.sort_values(by=['address'])

    # number of stakes attribute
    n_stakes = stakes.groupby(['staker']).size().reset_index(name='counter')

    # add DAO members
    for i, row in users.iterrows():
        st = n_stakes[n_stakes['staker'] == row['address']]
        st = 0 if len(st) == 0 else st['counter'].tolist()[0]

        nodes.append(
            (index, {'hash': row['address'], 'member': True, 'stakes': st})
        )
        hash_index[row['address']] = index
        dao_users.add(row['address'])
        index += 1

    # add non-DAO members
    stakers = set(stakes['staker'].tolist())
    non_users: Set[str] = stakers.difference(dao_users)

    for nu in non_users:
        st = n_stakes[n_stakes['staker'] == nu]
        st = 0 if len(st) == 0 else st['counter'].tolist()[0]
        nodes.append(
            (index, {'hash': nu, 'member': False, 'stakes': st})
        )
        hash_index[nu] = index
        index += 1

    return (nodes, hash_index)


def make_graph(users: pd.DataFrame, stakes: pd.DataFrame) -> nx.Graph:
    graph: nx.Graph = nx.Graph()

    nodes, hash_index = get_nodes_and_map(users=users, stakes=stakes)
    graph.add_nodes_from(nodes_for_adding=nodes)

    graph.add_weighted_edges_from(ebunch_to_add=get_edges_as_list(stakes=stakes, hash_index=hash_index))
    return graph


if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg, Genesis Alpha
    if len(sys.argv) != 2:
        print('ERROR: python staking_network.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]

    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users.reset_index(inplace=True)

    stakes: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'stakes.csv'), header=0)
    stakes = stakes[stakes['dao'] == dao_id]
    stakes.reset_index(inplace=True)

    nx.write_gml(make_graph(users=users, stakes=stakes), os.path.join('data', 'network', f'{sys.argv[1]}_stake.gml'))
