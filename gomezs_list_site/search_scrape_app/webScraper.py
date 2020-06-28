from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import json, math, re
import os
from django.conf import settings

GOOGLE_SECRET = settings.GOOGLE_SECRET
from search_scrape_app.cl_subdomains.usStateAbbrev import abbrev_us_state
from search_scrape_app.cl_subdomains.caProvAbbrev import abbrev_ca_prov

def scrapeCraigsList(search_query, where, cat="sss"):
    """
    Creates an HTMLSession so as to execute a few clicks on
    the page before rendering. This is to ensure that the
    <img> elements are actually showing as craigslist 
    usually initializes with list view w/o images
    """
    city_subdomain = getNearestCitySubdomain(where)
    session = HTMLSession()
    
    #  Click the gridview button twice - once to open drop down and
    # again to actually change view
    script="document.querySelector(\"#gridview\").click();" + \
    "document.querySelector(\"#gridview\").click();"
    
    r = session.get(formatQuery(city_subdomain, search_query, cat))
    r.html.render(script=script)
    content = r.html.find("div#sortable-results ul.rows", first=True).html
    resultsRows = BeautifulSoup(content,"html.parser")
    liTags = resultsRows.select("li.result-row")
    li_dicts = []

    for li in liTags:
        tmpDict = dict()
        tmpDict["img-src"] = li.select('a.result-image img')[0]["src"]
        resultInfo = li.select("p.result-info")[0]
        time = resultInfo.find("time")
        if time != []:
            time = time.get_text()
        tmpDict["time"] = time 

        a = resultInfo.select(".result-title");

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

    return li_dicts

def formatQuery(city_subdomain,search_query, category):
    """
    Formats the search query and any other params following the pattern used in 
    GET requests to /search/
    """
    url = city_subdomain + "/search/" + category + "?query=" + search_query
    return url

def getNearestCitySubdomain(location):
    # Given a location, returns the nearest city which has its own craigslist
    # subdomain
    subdomain_dict = loadSubdomainDict()
    
    #perform input validation

    # Use google places to check where "location" is
    placesUrl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    placesParams = {"input":location,
                    "inputtype":"textquery",
                    "fields":"formatted_address",
                    "key":GOOGLE_SECRET}
    r = requests.get(placesUrl, params=placesParams)
    placesJson = json.loads(r.content)

    ##### ERROR HANDLING YOU DUMMY!!!
    placesStatus = placesJson["status"]

    if placesStatus != "OK":
        # Handle errors here
        # What should be returned?
        print("Places API failure")
        print(json.dumps(placesJson, indent=2))
        raise Exception

    formatted_address = placesJson["candidates"][0]["formatted_address"]

    
    result_array = list(map(lambda s: s.strip(), formatted_address.split(",")))
    
    country = province = city = None
    
    resultsN = len(result_array)
    if resultsN < 1:
        return None
    country = result_array[-1]
    province = result_array[-2] if resultsN >= 2 else None

    pat = re.compile("[a-z]{0,}[\d]+", re.IGNORECASE)
    m = pat.search(province)
    if m != None:
        province = province[:m.start()].strip()

    #Currently unused but should be used to shortcircuit when possible
    city = result_array[-3] if resultsN >= 3 else None
    if country == ("USA" or "United States"):
        country = "US"
        if len(province) == 2:
            province = abbrev_us_state[province]
    elif country == "Canada" or country == "CA":
        country = "CA"
        # This needs to be its own object since I'm adding all of them
        if len(province) == 2:
            province = abbrev_ca_prov[province]
    
    countryNode = None
    if country in ["US", "CA"]:
        countryNode = subdomain_dict[country]
    else:
        if country in subdomain_dict["EU"].keys():
            countryNode = subdomain_dict["EU"][country]
        elif country in subdomain_dict["ASIA"]:
            countryNode = subdomain_dict["ASIA"][country]
        elif country in subdomain_dict["LATAM"]:
            countryNode = subdomain_dict["LATAM"][country]
        elif country in subdomain_dict["AF"]:
            countryNode = subdomain_dict["AF"][country]
        else:
            return None
    if len(countryNode.keys()) == 1:
        return list(countryNode.values())[0]

    provinceNode = countryNode.get(province)

    if type(provinceNode) == str:
        return provinceNode # Found a leaf node, can just return here
    if provinceNode == None:
        provinceNode = countryNode
        province = country
    
    #just search it here? Yeah fuck it thats where we're at god damn it
    candidate_list = [] # Only doing this because TECHNICALLY the keys aren't ordered
    for key in provinceNode.keys():
        candidate_list.append(key)
    distMatrixParams = {"origins": location + " " + province,
                        "key":GOOGLE_SECRET}
    candidateStr = "|".join(map(lambda s: s + " " +province, candidate_list))
    distMatrixParams["destinations"]=candidateStr
    distMatrixURL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    r_dist = requests.get(distMatrixURL, params=distMatrixParams)
    distJson = json.loads(r_dist.content)

    if distJson["status"] != "OK":
        # handle errors
        print(json.dumps(distJson, indent=2))
        raise Exception

    candidate_dists = list(map(distanceMatrixMap,
                            distJson.get("rows")[0].get('elements')))
    i = leastValueIndex(candidate_dists)
     
    return provinceNode.get(candidate_list[i])

def loadSubdomainDict():
    with open("search_scrape_app"+os.sep+"cl_subdomains" + os.sep + "cl_subdomains.json", "r") as f:
        jsontxt = f.read()
    subdomain_dict = json.loads(jsontxt)
    return subdomain_dict

def leastValueIndex(A):
    least = A[0]
    least_i = 0
    for i in range(len(A)):
        if least > A[i]:
            least_i = i
            least = A[i]
    return least_i

def distanceMatrixMap(elem):
    if elem["status"] != "OK":
        return math.inf

    result = elem.get('distance')
    if result == None:
        return math.inf
    
    result = result.get('value')
    if result == None:
        return math.inf
    return result

