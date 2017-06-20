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

    return "select * from csv where url='https://finance.yahoo.com/d/quotes.csv?s=" + symb + \
    "&f=nsl1c1d1t1ohgpv&e=.csv' and columns='name,symbol,price,change,date,time,open,high,low,close,volume'"


def makeWebhookResult(data):
    req = request.get_json(silent=True, force=True)
    action = req.get("result").get("action")
    
    # assigns all relevant stock values to their names
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    row = result.get('row')
    if row is None:
        return {}

    symbol = row.get("symbol")
    if symbol is None:
        return {}

    time = row.get('time')
    if time is None:
        return {}

    # The following two values aren't currently being used:
    date = row.get('date')
    if date is None:
        return {}

    name = row.get('name')
    if name is None:
        return {}

    price = row.get('price')
    if price is None:
        return {}

    change = row.get('change')
    if change is None:
        return {}

    open1 = row.get('open')
    if open1 is None:
        return {}

    high = row.get('high')
    if high is None:
        return {}

    low = row.get('low')
    if low is None:
        return {}

    close = row.get('close')
    if close is None:
        return {}

    volume = row.get('volume')
    if volume is None:
        return {}

    # print(json.dumps(item, indent=4))

    """speech = "The most recent price of " + symbol.upper() + " stock is $" + price + \
             ", and the change on the day is $" + change + "."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-stocks-webhook"
    }
    """# determines which answer to give with which values based on the question asked.
    if action == "price" or action == "change":
        speech = "The most recent price for " + name + " is $" + price
        if change[0:1] == "+":
            speech += "; they're up $" + change[1:] + " as of " + time + " today."
        elif change[0:1] == "-":
            speech += "; they're down $" + change[1:] + " as of " + time + " today."
        else: speech += "; the market is currently closed."
    
    elif action == "volume":
        speech = "The volume of " + name + " is " + volume + "."

    elif action == "open":
        speech = name + " most recently opened at " + open1 + "."

    elif action == "close":
        speech = name + " most recently closed at " + close + "."

    elif action == "high":
        speech = "The high for " + name + " today was " + high + "."

    elif action == "low":
        speech = "The low for " + name + " today was " + low + "."

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
