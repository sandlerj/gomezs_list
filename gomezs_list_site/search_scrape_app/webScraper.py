import requests_html import HTMLSession
from bs4 import BeautifulSoup
import os
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")

'''
This is going to need a lot of testing you twit
'''
def scrapeCraigsList(searchQuery, where, cat="sss"):
    """
    Creates an HTMLSession so as to execute a few clicks on
    the page before rendering. This is to ensure that the
    <img> elements are actually showing as craigslist 
    usually initializes with list view w/o images
    """
    city = nearestCity(where)
    session = HTMLSession()
    
    #  Click the gridview button twice - once to open drop down and
    # again to actually change view
    script="document.querySelector(\"#gridview\").click();" +
    "document.querySelector(\"#gridview\").click();"
    
    r = session.get(formatQuery(city, searchQuery, cat))
    r.html.render(script=script)
    content = r.html.find("div#sortable-results ul.rows", first=True).html
    resultsRows = BeautifulSoup(content,"html.parser")
    liTags = resultRows.select("li.result-row")
    li_dicts = []

    for li in liTags:
        tmpDict = dict()
        tmpDict["img-src"] = li.select('a.result-image img')[0]["src"]
        resultInfo = li.select("p.result-info")[0]
        time = resultInfo.find("time")
        if time != []:
            time = time.get_text()
        tmpDict["time"] = time 

        a = resultInfo.find(class="result-title")
        if a == []:
            continue # No data here somehow... don't include this one.
        link = a["href"]
        tmpDict["link"] = link
        title = a.get_text()
        tmpDict["title"] = title
        meta = resultInfo.select("span.result-meta")
        hood = meta.select("span.result-hood")
        if hood != []:
            hood = hood.get_text()[1:-1]
        tmpDict["hood"] = hood
        price = meta.select("span.result-price")
        if price != []:
            price = price.get_text()
        tmpDict["price"] = price

        li_dicts.append(tmpDict)
    retun li_dicts

def formatQuery(city,searchQuery, catergory):
"""
Formats the search query and any other params following the pattern used in 
GET requests to /search/
"""
    return

def nearestCity(location):
    # Given a location, returns the nearest city which has its own craigslist
    # subdomain
    return