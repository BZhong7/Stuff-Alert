import requests
import json
import os

def item_finder(event, context):
    for brand in event["brands"]:
        payload = {'api_key': os.environ['apikey'],
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

    print(data)
    return{
        "message": "Success!"
    }

