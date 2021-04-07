"""
   Descp: Filters a dataframe with a date

   Created on: 07-april-2021

   Copyright 2021-2022 Youssef 'FRYoussef' El Faqir El Rhazoui
        <f.r.youssef@hotmail.com>
"""

import pandas as pd
from datetime import datetime

def filter_date(df: pd.DataFrame, date_key: str, date: str) -> pd.DataFrame:
    dff: pd.DataFrame = df.copy()
    dff.loc[:, date_key] = pd.to_datetime(dff.loc[:, date_key], unit='s')

    filter_date: datetime = datetime.strptime(date, '%d/%m/%Y')
    dff.loc[:, :] = dff[dff[date_key] < filter_date]

    return dff.dropna()
