# Copyright (c) 2022 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# WebScrapper.py
# Description: Helper functions that enables a generic webscrapper 

from common.utils.tokenizer.signer import *
from common.utils.formatter.printer import *
import requests
from bs4 import BeautifulSoup



def scrap_from_website(url, findable_id):
    page = requests.get(url)
    soup =  BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id=findable_id)
    return results

def get_scrapped_list(scrapped_data):
    scrapped_list = []
    for item in scrapped_data: 
        scrapped_list.append(item.text)
    return scrapped_list



