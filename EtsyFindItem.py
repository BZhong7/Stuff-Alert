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

    try:
        eBayResponse = api.execute('findItemsByKeywords', api_request)

        eBayDict = {}
        for index, item in enumerate(eBayResponse.reply.searchResult.item):
            eBayDict[index] = {}
            eBayDict[index]["title"] = item.title
            eBayDict[index]["price"] = item.sellingStatus.currentPrice.value
            eBayDict[index]["url"] = item.viewItemURL
    except:
        eBayDict = {}
        eBayDict["error"] = "Unable to connect..."


#-----------------Etsy API--------------
    etsyDict = {}
    for brand in event["multiValueQueryStringParameters"]["brands"]:
        etsyDict[brand] = {}
        for tag in event["multiValueQueryStringParameters"]["tags"]:
            payload = {'api_key': os.environ['etsyapikey'],
                'fields':  'listing_id,title,price,url',
                'category': 'Clothing',
                'tags': tag,
                'keywords': brand}

            try:
                etsyResponse = requests.get('https://openapi.etsy.com/v2/listings/active?',
                        params=payload)

                etsyDict[brand][tag] = {}
                for index, x in enumerate(etsyResponse.json()["results"]):
                    etsyDict[brand][tag][index] = {}
                    etsyDict[brand][tag][index]["title"] = x["title"]
                    etsyDict[brand][tag][index]["price"] = x["price"]
                    etsyDict[brand][tag][index]["url"] = x["url"]
            except:
                etsyDict = {}
                etsyDict["error"] = "Unexpected error..."


#----------------Create and return response----------------

    responseObject = {}
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = "eBay: " + json.dumps(eBayDict, indent=4)
    responseObject['body'] += "\n" + "Etsy: " + json.dumps(etsyDict, indent=4)

    return responseObject
