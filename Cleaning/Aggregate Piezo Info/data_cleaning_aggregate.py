#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 22:50:13 2021

@author: aliasger
"""

#Importing required libraries

import pandas as pd
from googletrans import Translator
from pyproj import Proj, transform

#Setting translator for Spanish to English
translator = Translator()


#Meta data to handle raw data files
meta_data = pd.read_csv("/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/scrape_meta_data.csv")

meta_data = meta_data.to_dict()
meta_data_id = meta_data["ID"]


def esp_to_en(df):
    '''
    Converts column headers from Spanish to English.

    Parameters
    ----------
    raw_cp : Data Frame
        Raw Spanish data frame.

    Returns
    -------
    raw_cp : Data Frame
        Raw English data frame.

    '''
    
    col_sp = list(df.columns)
    col_en = []
    
    for i in range(len(col_sp)):
        col_en.append(translator.translate(col_sp[i]).text)
        
    col_en[2] = "Province"
    col_en[-4] = "Latitude"
    col_en[-3] = "Longitude"
    
    df.columns = col_en
    
    return df


def drop(df, drop_label):
    '''
    Drop the unnecesary columns from data frame.

    Parameters
    ----------
    df : Data Frame
        Undeleted column data frame.

    Returns
    -------
    df : Data Frame
        Necessary column data frame.

    '''
    
    for i in drop_label:
        df = df.drop(df.columns[i], axis=1)
    
    return df
    

def raw_changes(raw_cp):
    '''
    Does the required cleaning steps for the raw dataframe.

    Parameters
    ----------
    raw_cp : Data Frame
        Raw data frame.

    Returns
    -------
    raw_cp_del : Data Frame
        Cleaned data frame.

    '''
    
    raw_cp.columns = raw_cp.iloc[0]
    raw_cp = raw_cp.drop(raw_cp.index[[0]])
    
    drop_label = [4,4,6,6,7,-1,-1,-2]
    raw_cp_drop = drop(raw_cp, drop_label)
    
    return raw_cp_drop


def column(df):
    '''
    Creates the list of columns as per required for final aggregate dataframe.

    Parameters
    ----------
    df : Data Frame
        The dataframe on which cleaning has been done.

    Returns
    -------
    col : List
        List of columns required for aggregate dataframe.

    '''
    
    col = list(df.columns)
    col = col[:-1]
    col.append(' Measurement Start Date')
    col.append('Measurement Last Date')
    
    return col


def df_create():
    '''
    Generates the aggregate dataframe based on required columns after cleaning.

    Returns
    -------
    df : Dataframe
        The aggregate dataframe to which rows will be appended.

    '''
    
    meta_id = '06.08.001'
    path = "/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/Raw Data/"+str(meta_id)+".csv"
    raw = pd.read_csv(path) 
    raw_cp = raw.copy()
    raw_final = raw_changes(raw_cp)
    
    col = column(raw_final)
    
    df = pd.DataFrame(columns = col) 
    
    return df


def coord_tranform(x1,y1):
    '''
    The function transforms coordinates from UTM 90 code to latitude-longitude 
    coordinates.

    Parameters
    ----------
    x1 : Float
        UTM 90 type. - longitude equivalent
    y1 : TYPE
        UTM 90 type. - latitude equivalent

    Returns
    -------
    x2 : Float
        Longitude coordinate.
    y2 : Float
        Latitude coordinate.

    '''
    
    inProj = Proj('epsg:32630') #UTM 90 code
    outProj = Proj('epsg:4326') #latitude-longitude code
    
    x2,y2 = transform(inProj,outProj,x1,y1)
    
    return x2, y2


def data_append(df):
    '''
    
    The function extracts a row of data from raw dataframe to append to 
    aggregrate dataframe.

    Parameters
    ----------
    df : Data Frame
        The version of data frame for following change to apply.

    Returns
    -------
    row : List
        The row that is to be appended to aggregate dataframe.

    '''
    
    row = []
    col = column(df)
    
    for i in col[:-4]:
        row.append(df[i].iloc[0])
        
    x1 = int(df['Coordenada X (ETRS89)'].iloc[0].replace(".",""))
    y1 = int(df['Coordenada Y (ETRS89)'].iloc[0].replace(".",""))
    
    x2, y2 = coord_tranform(x1, y1)
    
    row.append(x2)
    row.append(y2)
    row.append(df['Fecha'].iloc[0])
    row.append(df['Fecha'].iloc[-1])
    
    dic_app = dict(zip(col, row))
    
    return dic_app
    

if __name__=="__main__":  
    
    # Creating dataframe for aggregate 
    df  = df_create()

    # Working with raw data 
    for meta_id in meta_data_id.values():
        path = "/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/Raw Data/"+str(meta_id)+".csv"
        raw = pd.read_csv(path) 
        raw_cp = raw.copy()
        raw_final = raw_changes(raw_cp)
        row = data_append(raw_final)
        df = df.append(row, ignore_index=True)
        
    
    df_final = esp_to_en(df)
    
    # Exporting the dataframe to csv
    if df_final.columns[3] == "Municipio":
        print("googletrans not working....\nTry again later!")
    else:
        df_final.to_csv("Piezometer_Info.csv")
    



