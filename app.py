#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "yahooStockData":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    symb = parameters.get("symbol")
    if symb is None:
    	symb = "AMZN"

    return "select * from csv where url='http://206.155.48.97/gvsi/xml/getdaily?fields=" + \
    "symbol,date,close&output=csv&includeheaders=false&symbol=AAPL&startdate=06-16-2017&enddate=06-17-2017/'"


def makeWebhookResult(data):
    req = request.get_json(silent=True, force=True)
    action = req.get("result").get("action")
    
    # assigns all relevant stock values to their names
    # date and symbol aren't being used
    query = data.get('query')
    result = query.get('results')
    row = result.get('row')
    name = row.get('name')
    symbol = row.get("symbol")
    price = row.get('price')
    change = row.get('change')
    date = row.get('date')
    time = row.get('time')
    open1 = row.get('open')
    high = row.get('high')
    low = row.get('low')
    close = row.get('close')
    volume = row.get('volume')
    
    if query is None or result is None or row is None or name is None or symbol is None \
    or price is None or change is None or date is None or time is None or open1 is None \
    or high is None or low is None or close is None or volume is None:
        return {}

    # print(json.dumps(item, indent=4))

    # determines which answer to give with which values based on the question asked.
    if action == "pricechange":
        speech = "The most recent price for " + name + " is $" + price
        if change[0:1] == "+":
            speech += "; they're up $" + change[1:] + " as of " + time + " today."
        elif change[0:1] == "-":
            speech += "; they're down $" + change[1:] + " as of " + time + " today."
        else: speech += "; the market is currently closed."
    
    elif action == "volume":
        speech = "The volume of " + name + " is " + volume + "."

    elif action == "openclose":
        speech = name + " most recently opened at $" + open1 + "; it most recently closed at $" + close + "."

    elif action == "highlow":
        speech = "The high for " + name + " today was $" + high + "; the low was $" + low + "."

    else: speech = "Error: Action requested is undefined."
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-stocks-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
