import json

from ebaysdk.finding import Connection as finding
from bs4 import BeautifulSoup

def finder_handler(event, context):

    search_terms = '('
    for x in event["brands"]:
        search_terms += '"' + x + '"' + ','
    search_terms += ')'

    Keywords = search_terms
    api = finding(config_file='ebay.yaml')
    api_request = { 'keywords': Keywords, 
            'paginationInput': {
                'entriesPerPage': 10,
                'pageNumber': 1
            },
            #aspectFilter is CASE SENSITIVE. Wording must also be EXACT.
            'aspectFilter': event["aspectFilters"]
        }
    response = api.execute('findItemsByKeywords', api_request)
    soup = BeautifulSoup(response.content,'lxml')

    totalentries = int(soup.find('totalentries').text)
    items = soup.find_all('item')

    dic={}

    for index, item in enumerate(items, start=1):
        cat = item.categoryname.string.lower()
        title = item.title.string.lower()
        price = int(round(float(item.currentprice.string)))
        url = item.viewitemurl.string.lower()

        dic[index] = {}
        dic[index]['cat'] = cat
        dic[index]['title'] = title
        dic[index]['price'] = price
        dic[index]['url'] = url

    print(json.dumps(dic, indent=4))

    return {
        'statusCode': 200,
        'body': json.dumps(dic)
    }
