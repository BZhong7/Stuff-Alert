import requests
import json
import os

from ebaysdk.finding import Connection as finding


def create_etsy_payload(brand, tag):
    if brand == "":
        payload = {'api_key': os.environ['etsyapikey'],
                   'fields': 'listing_id,title,price,url',
                   'keywords': tag
                   }
    else:
        payload = {'api_key': os.environ['etsyapikey'],
                   'fields': 'listing_id,title,price,url',
                   # 'category': 'Clothing',
                   'tags': brand,
                   'keywords': tag
                   }
    return payload


def create_aspect_filter(size):
    aspectFilter = []

    # aspectFilter is CASE SENSITIVE. Wording must also be EXACT.
    for x in size:
        aspectFilter.append({'aspectName': 'Size', 'aspectValueName': size})

    return aspectFilter


def create_pagination_input():
    pageObj = {'entriesPerPage': 10, 'pageNumber': 1}
    return pageObj


def item_finder(event, context):
    # -----------------eBay Finding API------------------
    eBayDict = {}
    for brand in event["multiValueQueryStringParameters"]["brands"]:
        eBayDict[brand] = {}
        for tag in event["multiValueQueryStringParameters"]["tags"]:
            search_terms = brand + " " + tag

            api = finding(appid=os.environ["ebayapikey"], config_file=None, https=True)
            try:
                if tag == "Pants" & len(event["multiValueQueryStringParameters"]["pantsSize"]) > 0:
                    api_request = {'keywords': search_terms,
                                   'paginationInput': create_pagination_input(),
                                   'aspectFilter': create_aspect_filter(
                                       event["multiValueQueryStringParameters"]["pantsSize"])
                                   }
                elif tag == "Shoes" & len(event["multiValueQueryStringParameters"]["shoeSize"]) > 0:
                    api_request = {'keywords': search_terms,
                                   'paginationInput': create_pagination_input(),
                                   'aspectFilter': create_aspect_filter(
                                       event["multiValueQueryStringParameters"]["shoeSize"])
                                   }
                elif tag == "Shirts" & len(event["multiValueQueryStringParameters"]["shirtSize"]) > 0:
                    api_request = {'keywords': search_terms,
                                   'paginationInput': create_pagination_input(),
                                   'aspectFilter': create_aspect_filter(
                                       event["multiValueQueryStringParameters"]["shirtSize"])
                                   }
            except:
                api_request = {'keywords': search_terms,
                               'paginationInput': create_pagination_input(),
                               }

            try:
                eBayResponse = api.execute('findItemsByKeywords', api_request)

                eBayDict[brand][tag] = {}
                for index, item in enumerate(eBayResponse.reply.searchResult.item):
                    eBayDict[brand][tag][index] = {}
                    eBayDict[brand][tag][index]["title"] = item.title
                    eBayDict[brand][tag][index]["price"] = item.sellingStatus.currentPrice.value
                    eBayDict[brand][tag][index]["url"] = item.viewItemURL
            except:
                eBayDict[brand][tag] = {}
                eBayDict[brand][tag]["error"] = "Error: No Results..."

    # -----------------Etsy API--------------
    etsyDict = {}
    for brand in event["multiValueQueryStringParameters"]["brands"]:
        # Etsy 'tags' seem to use APC instead of A.P.C., so change it to match Etsy.
        # Same for No Nationality -> NN07
        if brand == "A.P.C.":
            brand = "APC"
        elif brand == "No Nationality":
            brand = "NN07"
        etsyDict[brand] = {}

        for tag in event["multiValueQueryStringParameters"]["tags"]:
            payload = create_etsy_payload(brand, tag)

            try:
                if brand == "NN07":
                    brandAndTag = brand + " " + tag
                    payload = create_etsy_payload("", brandAndTag)
                    etsyResponse = requests.get('https://openapi.etsy.com/v2/listings/active?',
                                            params=payload)
                else:
                    etsyResponse = requests.get('https://openapi.etsy.com/v2/listings/active?',
                                                params=payload)

                etsyDict[brand][tag] = {}
                for index, x in enumerate(etsyResponse.json()["results"]):
                    etsyDict[brand][tag][index] = {}
                    etsyDict[brand][tag][index]["title"] = x["title"]
                    etsyDict[brand][tag][index]["price"] = x["price"]
                    etsyDict[brand][tag][index]["url"] = x["url"]
            except:
                etsyDict[brand][tag] = {}
                etsyDict[brand][tag]["error"] = "Unexpected error..."

    # ----------------Create and return response----------------

    responseObject = {}
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = "eBay: " + json.dumps(eBayDict, indent=4)
    responseObject['body'] += "\n" + "Etsy: " + json.dumps(etsyDict, indent=4)

    return responseObject
