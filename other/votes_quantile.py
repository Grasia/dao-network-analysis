"""
   Descp: Prints votes quantile

   Created on: 16-mar-2021

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
        print('ERROR: python vote_quantile.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]

    # users who vote
    voters: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'votes.csv'), header=0)
    voters = voters[voters['dao'] == dao_id]
    voters.reset_index(inplace=True)
    voters = filter_date(df=voters, date_key='createdAt', date='01/04/2021')
    voters = voters.groupby(['voter']).size().reset_index(name='votes')

    # all users
    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users.reset_index(inplace=True)
    users = filter_date(df=users, date_key='createdAt', date='01/04/2021')

    # calculate users who didnt vote
    users = set(users['address'].tolist())
    vote_users = set(voters['voter'].tolist())
    non_vote_users = users.difference(vote_users)

    # add non-vote-users to df
    for u in non_vote_users:
        voters = voters.append({'voter': u, 'votes': 0}, ignore_index=True)

    print(f'\nTotal votes = {sum(voters["votes"].tolist())}\n')
    print(f'{voters.quantile([.25, .5, .75, .90, .95, .99])}')