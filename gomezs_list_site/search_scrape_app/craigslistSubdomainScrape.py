import requests
from bs4 import BeautifulSoup
import json
import os

"""
This should be used to periodically ensure that the subdomain json is still
accurate, but only as part of occasional maintenance or if users report failed
scrape requests, indicating that one of the subdomain links is incorrect. This
should not be used a as a part of a normal process on the server because it will
take up lots of time and make users sad when everything is moving slow.
"""

def updateJson():
    subdomainDict = scrapeSubdomains()
    with open("cl_subdomains"+os.sep+"cl_subdomains.json", "w") as f:
        json.dump(subdomainDict, f)

def scrapeSubdomains():
    page = requests.get("https://www.craigslist.org/about/sites")
    soup = BeautifulSoup(page.content, "html.parser")
    h1Tags = soup.select("h1")
    subdomainDict = dict()
    stateDivs = soup.select("div.colmask div.box")
    h1Iter = iter(h1Tags)
    for i in range(len(stateDivs)):
        stateDiv = stateDivs[i]
        if "box_1" in stateDiv["class"]:
            h1Tag = next(h1Iter)
        
        country = h1Tag.select("a")[0]['name']
        if subdomainDict.get(country) == None:
            tmpCountryDict = subdomainDict[country] = dict()
        else:
            tmpCountryDict = subdomainDict[country]

        h4Tags = stateDiv.select("h4")
        stateUls = stateDiv.select("h4 + ul")
        assert(len(h4Tags) == len(stateUls))
        for j in range(len(h4Tags)):
            stateName = h4Tags[j]
            stateUl = stateUls[j]
            tmpStateDict = tmpCountryDict[stateName.get_text()] = dict()
            cities = stateUl.select("li a")
            for city in cities:
                cityKey = city.get_text().title()
                if "/" in cityKey:
                    cityKey = cityKey[:cityKey.find(" /")]
                tmpStateDict[cityKey] = city["href"]

    return subdomainDict



if __name__ == "__main__":
    updateJson()