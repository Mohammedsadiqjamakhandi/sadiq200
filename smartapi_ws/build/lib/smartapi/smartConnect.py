import requests, json, pyotp

class SmartConnect:
    def __init__(self, api_key):
        self.api_key = api_key
        self.jwt_token = None
        self.feed_token = None
        self.client_code = None

    def generate_session(self, client_code, password, totp_code):
        url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword"
        payload = {"clientcode": client_code, "password": password, "totp": totp_code}
        resp = requests.post(url, json=payload, headers={"Content-Type":"application/json"})
        data = resp.json()["data"]
        self.jwt_token = data["jwtToken"]
        self.feed_token = data["feedToken"]
        self.client_code = data["clientcode"]
        return data
