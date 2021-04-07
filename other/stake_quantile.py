"""
   Descp: Prints stakes quantile

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
        print('ERROR: python stake_quantile.py dao_name')
        exit(1)

    daos: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'daos.csv'), header=0)
    daos = daos[daos['name'] == sys.argv[1]]
    if len(daos) == 0:
        print('ERROR: DAO name not found.')
        exit(1)
    
    dao_id: str = daos['id'].tolist()[0]

    # stakers
    stakers: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'stakes.csv'), header=0)
    stakers = stakers[stakers['dao'] == dao_id]
    stakers.reset_index(inplace=True)
    stakers = filter_date(df=stakers, date_key='createdAt', date='01/04/2021')
    stakers = stakers.groupby(['staker']).size().reset_index(name='stakes')

    # all users
    users: pd.DataFrame = pd.read_csv(os.path.join('data', 'raw', 'reputation_holders.csv'), header=0)
    users = users[users['dao'] == dao_id]
    users.reset_index(inplace=True)
    users = filter_date(df=users, date_key='createdAt', date='01/04/2021')

    # calculate users who didnt stake
    users = set(users['address'].tolist())
    all_stakers = set(stakers['staker'].tolist())
    non_stake_users = users.difference(all_stakers)

    # add non-vote-users to df
    for u in non_stake_users:
        stakers = stakers.append({'staker': u, 'stakes': 0}, ignore_index=True)

    # remove non member stakers
    for i, row in stakers.iterrows():
        if row['staker'] not in users:
            stakers = stakers.drop(i)

    print(f'\nTotal stakes = {sum(stakers["stakes"].tolist())}\n')
    print(f'{stakers.quantile([.25, .5, .75, .90, .95, .99])}')