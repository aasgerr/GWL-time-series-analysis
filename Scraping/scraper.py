#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 02:42:03 2021

@author: aliasger
"""

# Importing relevant libraries
import pandas as pd
from selenium import webdriver
import os
import time

# Loading meta data from csv file
meta_data = pd.read_csv("scrape_meta_data.csv")

meta_data = meta_data.to_dict()
meta_data_id = meta_data["ID"]
meta_data_web = meta_data["Web No."]

record_no = len(meta_data_id)

# Setting up chromedriver profile for selenium
prefs = {
'download.default_directory': '/Users/aliasger/Desktop/Scraping',
'download.prompt_for_download': False,
'download.extensions_to_open': 'xml',
'safebrowsing.enabled': True
}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs',prefs)
options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--safebrowsing-disable-download-protection")
options.add_argument("safebrowsing-disable-extension-blacklist")
driver = webdriver.Chrome(options=options, executable_path=r'/usr/local/bin/chromedriver')

#Iterating and scraping through required piezometer data
for i in range(record_no):
    ID = meta_data_id[i]
    Web = meta_data_web[i]
    
    #https://sig.mapama.gob.es/WebServices/clientews/intranet/default.aspx?nombre=PIEZOMETROS&claves=DGAGUA.PIEZOMETROS.PIE_NUMPIE&valores=2980&origen=2&op=Exportar
    
    target_url = 'https://sig.mapama.gob.es/WebServices/clientews/intranet/default.aspx?nombre=PIEZOMETROS&claves=DGAGUA.PIEZOMETROS.PIE_NUMPIE&valores='+str(Web)+'&origen=2&op=Exportar'
    driver.get(target_url)
    
    time.sleep(5)
    
    uniqueName = str(ID)+".xml"
    os.rename("FichaExportacion.xml", uniqueName)

