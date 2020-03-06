import requests
import json
import os

def searchEtsyListing(searchWords):
    payload = {'api_key': os.environ['apikey'],
            'fields':  'listing_id,title,price,url',
            'category': 'Clothing',
            'keywords': searchWords}

    r = requests.get('https://openapi.etsy.com/v2/listings/active?', params=payload)

    data = {}
    json_file = r.json()
    for index, x in enumerate(json_file["results"]):
        data[index] = {}
        data[index]["title"] = x["title"]
        data[index]["price"] = x["price"]
        data[index]["url"] = x["url"]

    return { data }

def item_finder(event, context):
    print(searchEtsyListing("nike")
    #for index, x in enumerate(event["brands"]):
        #listings[index].append(searchEtsyListing(x))

    return{
        "message": "Success!"
    }
