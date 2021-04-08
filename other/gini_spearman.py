"""
   Descp: Calculates gini coefficientof various stats

   Created on: 07-april-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import os
import sys
import pandas as pd
from scipy.stats import spearmanr
from utils.time_filter import filter_date


def gini(list_of_values: list) -> float:
    sorted_list = sorted(list_of_values)
    height, area = 0, 0

    for value in sorted_list:
        height += value
        area += height - value / 2.

    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area


def get_data_frame(file: str, dao_id: str) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', file), header=0)
    df = df[df['dao'] == dao_id]
    return filter_date(df=df, date_key='createdAt', date='01/04/2021')


if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg, Genesis Alpha
    if len(sys.argv) != 2:
        print('ERROR: python reputation_plot.py dao_name')
        exit(1)

    dao_name: str = sys.argv[1]
    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == dao_name]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]

    reputation_holders: pd.DataFrame = get_data_frame(file='reputation_holders.csv', dao_id=dao_id)
    users = set(reputation_holders['address'].tolist())

    balances = []
    for i, row in reputation_holders.iterrows():
        balances.append(int(row['balance']))

    reputation_holders.pop('balance')
    reputation_holders['balance'] = balances

    votes: pd.DataFrame = get_data_frame(file='votes.csv', dao_id=dao_id)
    votes = votes.groupby(['voter']).size().reset_index(name='votes')

    proposals: pd.DataFrame = get_data_frame(file='proposals.csv', dao_id=dao_id)
    proposals = proposals.groupby(['proposer']).size().reset_index(name='proposals')

    stakes: pd.DataFrame = get_data_frame(file='stakes.csv', dao_id=dao_id)
    stakes = stakes.groupby(['staker']).size().reset_index(name='stakes')
    # remove non member stakers
    for i, row in stakes.iterrows():
        if row['staker'] not in users:
            stakes = stakes.drop(i)

    #if DAO is dxDAO or Genesis Alpha add network metrics
    show_centrality: bool = False
    if dao_name in {'dxDAO', 'Genesis Alpha'}:
        show_centrality = True

        votes_centrality: pd.DataFrame = pd.read_csv(
            os.path.join('data', 'network', 'centrality', f'{dao_name}_vote_centrality.csv'), header=0)
        stakes_centrality: pd.DataFrame = pd.read_csv(
            os.path.join('data', 'network', 'centrality', f'{dao_name}_stakes_centrality.csv'), header=0)

        # create dataframe with all the stats
        user_stats: dict = {
            u: {'Reputation': 0, 'Votes': 0, 'Proposals': 0, 'Stakes': 0, 'VotePageRank': 0, 'StakePageRank': 0}
        for u in users}

    else:
        # create dataframe with all the stats
        user_stats: dict = {
            u: {'Reputation': 0, 'Votes': 0, 'Proposals': 0, 'Stakes': 0}
        for u in users}

    # add reputation
    for i, row in reputation_holders.iterrows():
        user_stats[row['address']]['Reputation'] = row['balance']

    # add votes
    for i, row in votes.iterrows():
        if row['voter'] in user_stats: 
            user_stats[row['voter']]['Votes'] = row['votes']

    # add stakes
    for i, row in stakes.iterrows():
        user_stats[row['staker']]['Stakes'] = row['stakes']

    # add proposals
    for i, row in proposals.iterrows():
        if row['proposer'] in user_stats: 
            user_stats[row['proposer']]['Proposals'] = row['proposals']

    # add centrality measures if enabled
    if show_centrality:
        #add vote page rank
        for i, row in votes_centrality.iterrows():
            if row['hash'] in user_stats: 
                user_stats[row['hash']]['VotePageRank'] = row['pageranks']

        #add stake page rank
        for i, row in stakes_centrality.iterrows():
            if row['hash'] in user_stats: 
                user_stats[row['hash']]['StakePageRank'] = row['pageranks']

        # to dataframe
        user_stats: list = [
            {
                'Address': u, 
                'Reputation': user_stats[u]['Reputation'], 
                'Votes': user_stats[u]['Votes'], 
                'Proposals': user_stats[u]['Proposals'], 
                'Stakes': user_stats[u]['Stakes'],
                'VotePageRank': user_stats[u]['VotePageRank'],
                'StakePageRank': user_stats[u]['StakePageRank'],
            }
        for u in user_stats]

    else:
        # to dataframe
        user_stats: list = [
            {
                'Address': u, 
                'Reputation': user_stats[u]['Reputation'], 
                'Votes': user_stats[u]['Votes'], 
                'Proposals': user_stats[u]['Proposals'], 
                'Stakes': user_stats[u]['Stakes'],
            }
        for u in user_stats]

    user_stats: pd.DataFrame = pd.DataFrame(user_stats)

    print(f'Gini of reputation = {gini(list_of_values=user_stats["Reputation"].tolist())}.')
    print(f'Gini of votes = {gini(list_of_values=user_stats["Votes"].tolist())}.')
    print(f'Gini of proposals = {gini(list_of_values=user_stats["Proposals"].tolist())}.')
    print(f'Gini of stakes = {gini(list_of_values=user_stats["Stakes"].tolist())}.')

    if show_centrality:
        print(f'Gini of vote pagerank = {gini(list_of_values=user_stats["VotePageRank"].tolist())}.')
        print(f'Gini of stake pagerank = {gini(list_of_values=user_stats["StakePageRank"].tolist())}.\n')
    else:
        print('\n')

    rho1, p1 = spearmanr(user_stats['Reputation'], user_stats['Votes'])
    rho2, p2 = spearmanr(user_stats['Reputation'], user_stats['Proposals'])
    rho3, p3 = spearmanr(user_stats['Reputation'], user_stats['Stakes'])

    print(f'Spearman rank (Reputation-Votes) = {rho1}, p-value = {p1}.')
    print(f'Spearman rank (Reputation-Proposals) = {rho2}, p-value = {p2}.')
    print(f'Spearman rank (Reputation-Stakes) = {rho3}, p-value = {p3}.')

    if show_centrality:
        rho4, p4 = spearmanr(user_stats['Reputation'], user_stats['VotePageRank'])
        rho5, p5 = spearmanr(user_stats['Reputation'], user_stats['StakePageRank'])
        print(f'Spearman rank (Reputation-Vote Pagerank) = {rho4}, p-value = {p4}.')
        print(f'Spearman rank (Reputation-Stake Pagerank) = {rho5}, p-value = {p5}.')
