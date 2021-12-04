#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 02:49:34 2021

@author: aliasger
"""

import pandas as pd

meta_data = pd.read_csv("/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/scrape_meta_data.csv")

meta_data = meta_data.to_dict()
meta_data_id = meta_data["ID"]

for meta_id in meta_data_id.values():
    path = "/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/Raw Data/"+str(meta_id)+".csv"
    raw = pd.read_csv(path) 
    raw.columns = raw.iloc[0]
    raw = raw.drop(raw.index[[0]])

    raw_drop = raw

    for i in range(15):
        raw_drop = raw_drop.drop(raw_drop.columns[0], axis = 1)
    
    raw_drop.columns = ["Date","Level (m)","Dimension (m)"]
    raw_drop["Date"]= pd.to_datetime(raw_drop["Date"], dayfirst=True)
    raw_drop['Level (m)'] = raw_drop['Level (m)'].apply(lambda x: x.replace(',','.'))
    raw_drop['Dimension (m)'] = raw_drop['Dimension (m)'].apply(lambda x: x.replace(',','.'))
    raw_drop['Level (m)'] = raw_drop['Level (m)'].apply(pd.to_numeric)
    raw_drop['Dimension (m)'] = raw_drop['Dimension (m)'].apply(pd.to_numeric)
    raw_drop['Level (m)'] = raw_drop['Level (m)'].apply(pd.to_numeric)
    raw_drop['Dimension (m)'] = raw_drop['Dimension (m)'].apply(pd.to_numeric)
    
    raw_drop.to_csv(str(meta_id)+".csv")