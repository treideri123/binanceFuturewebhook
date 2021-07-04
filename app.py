from flask import Flask, request, Response
import requests
import json
import hmac
import hashlib
import time
import urllib
import logging

app = Flask(__name__)

logging.basicConfig(filename="log.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

@app.route('/')
def index():
    return 'Order Handler for Binance Futures & Binance Futures Testnet from Tradingview Signal'

@app.route('/exchange/binance/future/testnet', methods=['POST'])
def exchange_binance_future_testnet():
    if request.method == 'POST':
        try:
            logger.info("Binance Future Testnet: Started.")
            testnet_api_url = "https://testnet.binancefuture.com"
            testnet_api_key = "54b2c8cb2855070433906055aa677f729b82970644c1164a21fd74e35faac101"
            testnet_api_secret = "25b00f65f98b91cfa5d0bc73d91f2212f2e2c0a3ee5e9f975d8fecce071d5f86"
            testnet_exchangeInfo = "/fapi/v1/exchangeInfo"
            testnet_order = "/fapi/v1/order"
            tradingview_data = request.data
            jdata = json.loads(tradingview_data.decode('utf-8'))
            exchange = jdata["exchange"]
            symbol = jdata["ticker"].replace("PERP","")
            side = jdata["action"].upper()
            price = float(jdata["close"])
            quantity = 0.0
            if exchange == "BINANCE":
                if symbol != "":
                    if side == "BUY" or side == "SELL":
                        if price > 0:
                            exchangeInfo_response = requests.get("{}{}".format(testnet_api_url, testnet_exchangeInfo))
                            exchangeInfo_json = exchangeInfo_response.json()
                            if exchangeInfo_response.status_code == 200:
                                for symbols in exchangeInfo_json["symbols"]:
                                    if symbols["symbol"] == symbol:
                                        for filters in symbols["filters"]:
                                            if filters["filterType"] == "LOT_SIZE":
                                                quantity = float(filters["minQty"])
                                if quantity > 0:
                                    headers = {
                                        "X-MBX-APIKEY" : testnet_api_key
                                        }
                                    payload = {
                                        "symbol" : "{}".format(symbol),
                                        "side" : "{}".format(side),
                                        "price" : price,
                                        "quantity" : quantity,
                                        "type" : "LIMIT",
                                        "timeInForce":"GTC",
                                        "newClientOrderId" : "tradingview-{}-{}".format(side, int(time.time()))
                                        }
                                    payload["timestamp"] = str(int(time.time()*1000))
                                    query_string = urllib.parse.urlencode(payload)
                                    payload["signature"] = hmac.new(testnet_api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
                                    order_response = requests.post("{}{}".format(testnet_api_url, testnet_order), headers = headers, data = payload)
                                    order_json = order_response.json()
                                    if order_response.status_code == 200:
                                        logger.info(order_response.status_code)
                                        logger.info(order_json)
                                    else:
                                        logger.error(order_response.status_code)
                                        logger.error(order_json)
                                    telegram_api_url = "https://api.telegram.org/bot"
                                    telegram_getMe = "/getMe"
                                    telegram_getUpdates = "/getUpdates"
                                    telegram_sendMessage = "/sendMessage"
                                    telegram_api_token = "619525725:AAFaeUlh53ssop96tyIC2cGoD63kKa8szh0"
                                    getMe_response = requests.get("{}{}{}".format(telegram_api_url, telegram_api_token, telegram_getMe))
                                    getMe_json = getMe_response.json()
                                    if getMe_response.status_code == 200:
                                        if getMe_json["result"]["is_bot"] == True:
                                            print("Me is IS BOT true")
                                            getUpdates_response = requests.get("{}{}{}".format(telegram_api_url, telegram_api_token, telegram_getUpdates))
                                            getUpdates_json = getUpdates_response.json()
                                            if getUpdates_response.status_code == 200:
                                                if getUpdates_json["ok"] == True:
                                                    print("Updates is OK true")
                                                    chat_id = None
                                                    for result in getUpdates_json["result"]:
                                                        chat_id = result["message"]["from"]["id"]
                                                    if chat_id != None:
                                                        sendMessage_response = requests.get("{}{}{}?chat_id={}&text={}".format(telegram_api_url, telegram_api_token, telegram_sendMessage, chat_id, order_json))
                                                        sendMessage_json = sendMessage_response.json()
                                                        if sendMessage_response.status_code == 200 :
                                                            if sendMessage_json["ok"] == True:
                                                                logger.info("Message is OK true")
                                                            else:
                                                                logger.info("Message is OK false")
                                                else:
                                                    logger.info("Updates is OK false")
                                            else:
                                                logger.info("GetUpdates", getUpdates_response.status_code, getUpdates_json)
                                        else:
                                            logger.info("Me is IS BOT false")
                                    else:
                                        logger.info("GetMe", getMe_response.status_code, getMe_json)
                                else:
                                    logger.log("Invalid Order Quantity")
                            else:
                                logger.error(exchangeInfo_response.status_code)
                                logger.error(exchangeInfo_json)
                        else:
                            logger.info("CLOSE not defined from tradingview alert.")
                    else:
                        logger.info("BUY -or- SELL not defined from tradingview alert.")
                else:
                    logger.info("SYMBOL not defined from tradingview alert.")
            else:
                logger.info("EXCHANGE not defined from tradingview alert.")
        except:
            logger.exception("Binance Future Testnet: Exception Occurred.")
        finally:
            logger.info("Binance Future Testnet: Executed.")
            responseData = {
                "status" : True
                }
            return Response(json.dumps(responseData), status=200, mimetype='application/json')        
    else:
        logger.warning("API accessed in GET")
        responseData = {
            "status" : False
            }
        return Response(json.dumps(responseData), status=404, mimetype='application/json')

@app.route('/exchange/binance/future', methods=['POST'])
def exchange_binance_future():
    if request.method == 'POST':
        try:
            logger.info("Binance Future : Started.")
            testnet_api_url = "https://fapi.binance.com"
            testnet_api_key = "54b2c8cb2855070433906055aa677f729b82970644c1164a21fd74e35faac101"
            testnet_api_secret = "25b00f65f98b91cfa5d0bc73d91f2212f2e2c0a3ee5e9f975d8fecce071d5f86"
            testnet_exchangeInfo = "/fapi/v1/exchangeInfo"
            testnet_order = "/fapi/v1/order"
            tradingview_data = request.data
            jdata = json.loads(tradingview_data.decode('utf-8'))
            exchange = jdata["exchange"]
            symbol = jdata["ticker"].replace("PERP","")
            side = jdata["action"].upper()
            price = float(jdata["close"])
            quantity = 0.0
            if exchange == "BINANCE":
                if symbol != "":
                    if side == "BUY" or side == "SELL":
                        if price > 0:
                            exchangeInfo_response = requests.get("{}{}".format(testnet_api_url, testnet_exchangeInfo))
                            exchangeInfo_json = exchangeInfo_response.json()
                            if exchangeInfo_response.status_code == 200:
                                for symbols in exchangeInfo_json["symbols"]:
                                    if symbols["symbol"] == symbol:
                                        for filters in symbols["filters"]:
                                            if filters["filterType"] == "LOT_SIZE":
                                                quantity = float(filters["minQty"])
                                if quantity > 0:
                                    headers = {
                                        "X-MBX-APIKEY" : testnet_api_key
                                        }
                                    payload = {
                                        "symbol" : "{}".format(symbol),
                                        "side" : "{}".format(side),
                                        "price" : price,
                                        "quantity" : quantity,
                                        "type" : "LIMIT",
                                        "timeInForce":"GTC",
                                        "newClientOrderId" : "tradingview-{}-{}".format(side, int(time.time()))
                                        }
                                    payload["timestamp"] = str(int(time.time()*1000))
                                    query_string = urllib.parse.urlencode(payload)
                                    payload["signature"] = hmac.new(testnet_api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
                                    order_response = requests.post("{}{}".format(testnet_api_url, testnet_order), headers = headers, data = payload)
                                    order_json = order_response.json()
                                    if order_response.status_code == 200:
                                        logger.info(order_response.status_code)
                                        logger.info(order_json)
                                    else:
                                        logger.error(order_response.status_code)
                                        logger.error(order_json)
                                    telegram_api_url = "https://api.telegram.org/bot"
                                    telegram_getMe = "/getMe"
                                    telegram_getUpdates = "/getUpdates"
                                    telegram_sendMessage = "/sendMessage"
                                    telegram_api_token = "619525725:AAFaeUlh53ssop96tyIC2cGoD63kKa8szh0"
                                    getMe_response = requests.get("{}{}{}".format(telegram_api_url, telegram_api_token, telegram_getMe))
                                    getMe_json = getMe_response.json()
                                    if getMe_response.status_code == 200:
                                        if getMe_json["result"]["is_bot"] == True:
                                            print("Me is IS BOT true")
                                            getUpdates_response = requests.get("{}{}{}".format(telegram_api_url, telegram_api_token, telegram_getUpdates))
                                            getUpdates_json = getUpdates_response.json()
                                            if getUpdates_response.status_code == 200:
                                                if getUpdates_json["ok"] == True:
                                                    print("Updates is OK true")
                                                    chat_id = None
                                                    for result in getUpdates_json["result"]:
                                                        chat_id = result["message"]["from"]["id"]
                                                    if chat_id != None:
                                                        sendMessage_response = requests.get("{}{}{}?chat_id={}&text={}".format(telegram_api_url, telegram_api_token, telegram_sendMessage, chat_id, order_json))
                                                        sendMessage_json = sendMessage_response.json()
                                                        if sendMessage_response.status_code == 200 :
                                                            if sendMessage_json["ok"] == True:
                                                                logger.info("Message is OK true")
                                                            else:
                                                                logger.info("Message is OK false")
                                                else:
                                                    logger.info("Updates is OK false")
                                            else:
                                                logger.info("GetUpdates", getUpdates_response.status_code, getUpdates_json)
                                        else:
                                            logger.info("Me is IS BOT false")
                                    else:
                                        logger.info("GetMe", getMe_response.status_code, getMe_json)
                                else:
                                    logger.log("Invalid Order Quantity")
                            else:
                                logger.error(exchangeInfo_response.status_code)
                                logger.error(exchangeInfo_json)
                        else:
                            logger.info("CLOSE not defined from tradingview alert.")
                    else:
                        logger.info("BUY -or- SELL not defined from tradingview alert.")
                else:
                    logger.info("SYMBOL not defined from tradingview alert.")
            else:
                logger.info("EXCHANGE not defined from tradingview alert.")
        except:
            logger.exception("Binance Future : Exception Occurred.")
        finally:
            logger.info("Binance Future : Executed.")
            responseData = {
                "status" : True
                }
            return Response(json.dumps(responseData), status=200, mimetype='application/json')        
    else:
        logger.warning("API accessed in GET")
        responseData = {
            "status" : False
            }
        return Response(json.dumps(responseData), status=404, mimetype='application/json')

if __name__ == '__main__':
   app.run()
