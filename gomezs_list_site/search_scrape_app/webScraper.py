import requests_html import HTMLSession
from bs4 import BeautifulSoup

def scrapeCraigsList(searchQuery, city):
    """
    Creates an HTMLSession so as to execute a few clicks on
    the page before rendering. This is to ensure that the
    <img> elements are actually showing as craigslist 
    usually initializes with list view w/o images
    """
    session = HTMLSession()
    
    """
     Click the gridview button twice - once to open drop down and
    again to actually change view
    """
    script="document.querySelector(\"#gridview\").click();" +
    "document.querySelector(\"#gridview\").click();"
    
    r = session.get(formatQuery(city, searchQuery))
    r.html.render(script=script)
    content = r.html.find("div#sortable-results ul.rows", first=True).html
    resultsRows = BeautifulSoup(content,"html.parser")
    liTags = resultRows.select("li.result-row")


def formatQuery(city,searchQuery, type="sss"):
"""
Formats the search query and any other params following the pattern used in 
GET requests to /search/
"""
    return