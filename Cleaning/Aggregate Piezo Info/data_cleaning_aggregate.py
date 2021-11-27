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
import sys

#Setting translator for Spanish to English
translator = Translator()


#Meta data to handle raw data files
meta_data = pd.read_csv("/Users/aliasger/Desktop/Github/GWL-time-series-analysis/Scraping/scrape_meta_data.csv")

meta_data = meta_data.to_dict()
meta_data_id = meta_data["ID"]


def esp_to_en(raw_cp):
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
    
    col_sp = list(raw_cp.columns)
    col_en = []
    
    for i in range(len(col_sp)):
        col_en.append(translator.translate(col_sp[i]).text)
        
    col_en[2] = "Province"
    col_en[-2] = "Level (m)"
    col_en[-1] = "Dimension (m)"
    
    raw_cp.columns = col_en
    
    return raw_cp


def insert_decimal(raw_cp):
    '''
    Removes the commas to insert decimals.

    Parameters
    ----------
    raw_cp : Data Frame
        The CSV style data frame.

    Returns
    -------
    raw_cp : Data Frame
        Decimal inserted data frame.

    '''
    
    raw_cp = raw_cp.apply(lambda x: x.str.replace(',','.'))
    raw_cp['Level (m)'] = raw_cp['Level (m)'].apply(pd.to_numeric)
    raw_cp['Dimension (m)'] = raw_cp['Dimension (m)'].apply(pd.to_numeric)
    raw_cp['Level (m)'] = raw_cp['Level (m)'].apply(pd.to_numeric)
    raw_cp['Dimension (m)'] = raw_cp['Dimension (m)'].apply(pd.to_numeric)
    
    return raw_cp


def deletion(raw_cp):
    '''
    Deletes the unnecesary columns from data frame.

    Parameters
    ----------
    raw_cp : Data Frame
        Undeleted column data frame.

    Returns
    -------
    raw_cp : TYPE
        Necessary column data frame.

    '''
    
    try:
        del raw_cp['Date Level']
        del raw_cp['Groundwater body on which the piezometer is located']
        del raw_cp['Description']
        del raw_cp['Depth (m)']
        del raw_cp['No. of measures']
        del raw_cp['Hydrogeological Unit']
    except:
        sys.exit("googletrans not working right now...\n Try again later!")
    
    return raw_cp
    

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
    raw_cp_en = esp_to_en(raw_cp)
    raw_cp_dec = insert_decimal(raw_cp_en)
    raw_cp_del = deletion(raw_cp_dec)
    
    return raw_cp_del


def column(raw_cp):
    '''
    Creates the list of columns as per required for final aggregate dataframe.

    Parameters
    ----------
    raw_cp : Data Frame
        The dataframe on which cleaning has been done.

    Returns
    -------
    col : List
        List of columns required for aggregate dataframe.

    '''
    
    col = list(raw_cp.columns)
    col = col[0:-5]
    col.append('Longitude')
    col.append('Latitude')
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
    
    df = pd.DataFrame(columns = column(raw_final)) 
    
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


def data_append(raw_cp):
    '''
    
    The function extracts a row of data from raw dataframe to append to 
    aggregrate dataframe.

    Parameters
    ----------
    raw_cp : Data Frame
        The version of data frame for following change to apply.

    Returns
    -------
    row : List
        The row that is to be appended to aggregate dataframe.

    '''
    
    row = []
    col = column(raw_cp)
    
    for i in col[:-4]:
        row.append(raw_cp[i].iloc[0])
        
    x1 = int(raw_cp['X coordinate (ETRS89)'].iloc[0].replace(".",""))
    y1 = int(raw_cp['Y coordinate (ETRS89)'].iloc[0].replace(".",""))
    
    x2, y2 = coord_tranform(x1, y1)
    
    row.append(x2)
    row.append(y2)
    row.append(raw_cp['Date'].iloc[0])
    row.append(raw_cp['Date'].iloc[-1])
    
    return row
    

if __name__=="__main__":  
    
    # Creating dataframe for aggregate 
    df  = df_create()

    # Working with raw data 
    for meta_id in meta_data_id.values():
        path = "Scraping/Raw Data/"+str(meta_id)+".csv"
        raw = pd.read_csv(path) 
        raw_cp = raw.copy()
        raw_final = raw_changes(raw_cp)
        row = data_append(raw_final)
        df.loc[len(df.index)] = row
    
    # Exporting the dataframe to csv
    df.to_csv("Piezometer_Info.csv")
    



