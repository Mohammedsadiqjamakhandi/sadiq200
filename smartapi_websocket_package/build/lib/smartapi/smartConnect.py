import pyotp
import requests
import json
import logging

class SmartConnect:
    def __init__(self, api_key):
        self.api_key = api_key
        self.jwt_token = None
        self.refresh_token = None
        self.feed_token = None
        self.client_code = None

    def generate_session(self, client_code, password, totp):
        url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword"
        headers = {"Content-Type": "application/json"}
        payload = {
            "clientcode": client_code,
            "password": password,
            "totp": totp
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        self.jwt_token = data["data"]["jwtToken"]
        self.refresh_token = data["data"]["refreshToken"]
        self.feed_token = data["data"]["feedToken"]
        self.client_code = data["data"]["clientcode"]
        return data

    def get_ltp_data(self, exchange, symboltoken, tradingsymbol):
        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/order/v1/getLtpData"
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.api_key
        }
        payload = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "tradingsymbol": tradingsymbol
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()