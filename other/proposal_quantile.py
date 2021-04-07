"""
   Descp: Prints proposers quantile

   Created on: 07-april-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import pandas as pd
import os
import sys
from utils.time_filter import filter_date

if __name__ == '__main__':
    # Target DAOs --> dxDAO, dOrg, Genesis Alpha
    if len(sys.argv) != 2:
        print('ERROR: python proposal_quantile.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]

    # users who vote
    proposers: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'proposals.csv'), header=0)
    proposers = proposers[proposers['dao'] == dao_id]
    proposers.reset_index(inplace=True)
    proposers = filter_date(df=proposers, date_key='createdAt', date='01/04/2021')
    proposers = proposers.groupby(['proposer']).size().reset_index(name='proposals')

    # all users
    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users.reset_index(inplace=True)
    users = filter_date(df=users, date_key='createdAt', date='01/04/2021')

    # calculate users who didnt vote
    users = set(users['address'].tolist())
    proposer_users = set(proposers['proposer'].tolist())
    non_proposer_users = users.difference(proposer_users)

    # add non-vote-users to df
    for u in non_proposer_users:
        proposers = proposers.append({'proposer': u, 'proposals': 0}, ignore_index=True)

    print(f'\nTotal proposals = {sum(proposers["proposals"].tolist())}')
    print(f'\nMembers who have proposed at least once = {len(proposer_users)/len(users)*100:3.2f}%\n')
    print(f'{proposers.quantile([.25, .5, .75, .90, .95, 1])}')