import requests
import json
import os

from ebaysdk.finding import Connection as finding

def item_finder(event, context):

#-----------------eBay Finding API------------------    
    search_terms = '('
    for x in event["multiValueQueryStringParameters"]["brands"]:
        search_terms += '"' + x + '"' + ','
    search_terms += ')'

    Keywords = search_terms
    api = finding(appid=os.environ["ebayapikey"], config_file=None)
    api_request = { 'keywords': Keywords, 
            'paginationInput': {
                'entriesPerPage': 10,
                'pageNumber': 1
            }
            #aspectFilter is CASE SENSITIVE. Wording must also be EXACT.
            #'aspectFilter': event["aspectFilters"]
        }
    eBayResponse = api.execute('findItemsByKeywords', api_request)

    eBayDict = {}
    for index, item in enumerate(eBayResponse.reply.searchResult.item):
        eBayDict[index] = {}
        eBayDict[index]["title"] = item.title
        eBayDict[index]["price"] = item.sellingStatus.currentPrice.value
        eBayDict[index]["url"] = item.viewItemURL


#-----------------Etsy API--------------
    for brand in event["multiValueQueryStringParameters"]["brands"]:
        payload = {'api_key': os.environ['etsyapikey'],
            'fields':  'listing_id,title,price,url',
            'category': 'Clothing',
            'keywords': brand}

        etsyResponse = requests.get('https://openapi.etsy.com/v2/listings/active?', params=payload)

        etsyDict = {}
        #json_file = r.json()
        for index, x in enumerate(etsyResponse.json()["results"]):
            etsyDict[index] = {}
            etsyDict[index]["title"] = x["title"]
            etsyDict[index]["price"] = x["price"]
            etsyDict[index]["url"] = x["url"]


#----------------Create and return response----------------

    responseObject = {}
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body']['ebay'] = json.dumps(eBayDict)
    responseObject['body']['etsy'] = json.dumps(etsyDict)

    return responseObject
