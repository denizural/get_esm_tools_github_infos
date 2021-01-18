#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_esm_tools_github_infos

This scripts scrapes the main ESM-Tools GitHub repository page and extracts 
information such as number of issues / pull requests, etc.

The information is displayed as a pandas dataframe.

TODO: 
    - add CLI for ordering the dataframe
    
Deniz Ural, 11/01/2021
deniz.ural@awi.de
"""

from datetime import datetime
import re
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate

def parse_time(update_time_str):
    """Parse the time in HTML document into a more readable one. Convert the update time into last modified time.
    
    Parameters
    ----------
    update_time_str : str
        date string

    Returns
    -------
    return_str : str
        modified time date string with a better format
    """
    # regex groups:                 1   2  3   4  5 6    
    # time string has the format "2021-01-11T12:24:25Z"
    pattern = r'^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z.*$'
    match_obj = re.match(pattern, update_time_str)    
    year, month, day, hour, minute, second = map(int, match_obj.groups())
    
    update_time_obj = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    time_diff = datetime.now() - update_time_obj
    
    time_diff_days = time_diff.days
    time_diff_hours = (time_diff.seconds // 3600) % 24
    time_diff_minutes = (time_diff.seconds // 60) % 60
    time_diff_seconds = time_diff.seconds % 60
    
    return_str = ""
    if time_diff_days > 0:
        return_str += f"{time_diff_days} days"
    elif time_diff_hours > 0:
        return_str += f"{time_diff_hours} hours {time_diff_minutes} minutes"
    else:
        return_str += f"{time_diff_minutes} minutes {time_diff_seconds} seconds"
    
    return return_str


# start the timer
start = time.process_time()

# URL of the ESM-Tools packages
url = f"https://github.com/esm-tools"

# request and parse the GitHub page of the selected tool
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# repositor division, unordered list (ul) and list items (li)
repo_div = soup.find("div", {"id" : "org-repositories"})
uls = repo_div.find("ul")
lis = uls.find_all("li")

tools = []                      # list of strings
number_of_issues = []           # list of ints
number_of_pulls_requests = []   # list of ints
last_updated = []               # list of strings

# each list item corresponds to a ESM-Tools package
for li in lis:
    element = li.find("a", {"itemprop" : "name codeRepository"})
    
    # get the tool's name
    tools.append(element.text.strip())
    links = li.find_all('a', href=True)
    for link in links: 
        # get the number of issues
        if link['href'].endswith("issues"):
            number_of_issues.append(int(link.text.strip()))
        
        # get the number of pull requests
        if link['href'].endswith("pulls"):
            number_of_pulls_requests.append(int(link.text.strip()))
    
    # get the last modification time
    spans = li.find_all('span', class_="no-wrap")
    for span in spans:
        rel_time = span.find('relative-time').get('datetime')
        last_updated.append(parse_time(rel_time))

# create a Data Frame from the information gathered
df = pd.DataFrame(list(zip(number_of_issues, number_of_pulls_requests, last_updated)), 
                  columns = ['number of issues', 'number of pull requests', 'last updated'], index=tools)

# df.style.hide_index()
df.index.rename('tool name', inplace=True) 

# sort the data frame based on number of issues / pull requests
# df.sort_values(by = "number of pull requests", ascending=True, inplace=True)
df.sort_values(by = "number of issues", ascending=False, inplace=True)

# print the elapsed time and the table
print(time.process_time() - start)
print(tabulate(df, headers='keys', tablefmt='psql'))