import requests
import json
import os

from ebaysdk.finding import Connection as finding

def ebay_listing(event):
    search_terms = '('
    for x in event["brands"]:
        search_terms += '"' + x + '"' + ','
    search_terms += ')'

    Keywords = search_terms
    api = finding(appid=os.environ["ebayapikey"], config_file=None)
    api_request = { 'keywords': Keywords, 
            'paginationInput': {
                'entriesPerPage': 10,
                'pageNumber': 1
            },
            #aspectFilter is CASE SENSITIVE. Wording must also be EXACT.
            'aspectFilter': event["aspectFilters"]
        }
    response = api.execute('findItemsByKeywords', api_request)

    eBayDict = {}
    for index, item in enumerate(response.reply.searchResult.item):
        eBayDict[index] = {}
        eBayDict[index]["title"] = item.title
        eBayDict[index]["price"] = item.sellingStatus.currentPrice.value
        eBayDict[index]["url"] = item.viewItemURL
    
    print(json.dumps(eBayDict, indent=4))
    return { json.dumps(eBayDict) }
 
#----------------------------------------------------------------
def etsy_listing(event):
    for brand in event["brands"]:
        payload = {'api_key': os.environ['etsyapikey'],
            'fields':  'listing_id,title,price,url',
            'category': 'Clothing',
            'keywords': brand}

        r = requests.get('https://openapi.etsy.com/v2/listings/active?', params=payload)

        data = {}
        json_file = r.json()
        for index, x in enumerate(json_file["results"]):
            data[index] = {}
            data[index]["title"] = x["title"]
            data[index]["price"] = x["price"]
            data[index]["url"] = x["url"]

    print(json.dumps(data, indent=4))
    return { json.dumps(data) }

def item_finder(event, context):
    ebay_str = ebay_listing(event)
    etsy_str = etsy_listing(event)
    return{
        "message": "Success!"
    }
