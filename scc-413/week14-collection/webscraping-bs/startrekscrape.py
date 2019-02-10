#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin #https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin
from bs4 import BeautifulSoup, Tag #https://www.crummy.com/software/BeautifulSoup/bs4/doc/

base_url = "https://en.wikipedia.org/wiki/List_of_Star_Trek:_The_Original_Series_episodes"
#load webpage
req = requests.get(base_url)
#Use beautiful soup to decode webpage text into parseable document.
soup = BeautifulSoup(req.text, "html.parser")

episodes = []

#find and loop through all tds (table cells) with class name ``summary'' (which we know is an episode title)
for episode_cell in soup.find_all('td', {'class': 'summary'}):
    if episode_cell.a: #If there is an anchor, i.e. link...
        title = episode_cell.a.text.strip() #Get the actual text from the cell.
        episode_url = episode_cell.a['href'] #extract the url
        episode_url = urljoin(base_url,episode_url) #Use urljoin to make the URL absolute, by using the base_url as a reference.
        print("%s: %s" % (title, episode_url)) #demoing the extraction of title and url

        episode_plot = ""
        episode_req = requests.get(episode_url) #do a new request for the episode page.
        episode_soup = BeautifulSoup(episode_req.text, "html.parser") #use beautiful soup to decode into a parseable document.
        for h2 in episode_soup.find_all("h2"): #Go through all of the h2 elements.
            if(h2.text.strip().startswith("Plot")): #This is the h2 With "Plot" (and "Plot Summary")
                node = h2.next_sibling #start looking for tags after the Plot h2, will be strings and Tags.
                while True:
                    if isinstance(node, Tag): #Check if this element is actually a Tag.
                        if node.name == "p": #p tag, we want this.
                            episode_plot += node.text.strip() + "\n" #append the tag from p.
                        elif node.name == "h2": #at the next h2, so a new section, no longer the plot. Stop processing.
                            break
                    node = node.next_sibling #get next element at same level.

        episodes.append({'title': title, 'url': episode_url, 'plot': episode_plot}) #output the title, url and plot - in dictionary format, nice for JSON.

print(json.dumps(episodes,indent=4)) #print out the resulting json (pretty printed). Simple to change to outputting to file (see e.g. Twitter task: tweets_json)
