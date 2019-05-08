import requests
import json
import time
from base64 import b64encode
from pathlib import Path


class SierraAPI:

    # Sierra API client

    def __init__(self, apiURL, apiKey, apiSecret, debugMode=False):
        self.apiURL = apiURL
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.debugMode = debugMode

        self.token = None
        self.tokenExpiration = 0
        self.tokenMinLife = 10

        self.cacheFile = "token.json"

        cacheFile = Path(self.cacheFile)
        if cacheFile.is_file():
            with open(str(cacheFile), 'r') as file:
                token = json.load(file)
                self.token = token['access_token']
                self.tokenExpiration = token['expiration_time']

    def getToken(self):

        if (self.tokenExpiration - time.time()) < self.tokenMinLife:
            apiEncodedKey = b64encode(str.encode(self.apiKey + ':' + self.apiSecret))
            response = requests.post(self.apiURL + 'token',
                headers={'Authorization': 'Basic ' + str(apiEncodedKey, 'utf-8')},
                data={'grant_type': 'client_credentials'})

            self.token = response.json()['access_token']
            self.tokenExpiration = time.time() + response.json()['expires_in']

            if self.cacheFile:
                data = response.json()
                data['expiration_time'] = self.tokenExpiration
                cacheFile = Path(self.cacheFile)
                cacheFile.write_text(json.dumps(data, indent=4))

        if self.debugMode:
            print('Token: ' + self.token)
            print('Expires in: ' + str(self.tokenExpiration - time.time()))

    def get(self, path, params={}):
        self.getToken()
        response = requests.get(path,
            headers={'Authorization': 'Bearer ' + self.token},
            params=params)

        if self.debugMode:
            print(json.dumps(response.json(), indent=4))

        return response

    def post(self, path, params={}, data={}):
        self.getToken()
        response = requests.post(path,
                                headers={'Authorization': 'Bearer ' + self.token},
                                params=params,
                                data=data)

        if self.debugMode:
            try:
                print(json.dumps(response.json(), indent=4))
            except:
                print("Empty response")

        return response

    def put(self, path, params={}, data={}):
        self.getToken()
        response = requests.put(path,
                                headers={'Authorization': 'Bearer ' + self.token},
                                params=params,
                                data=data)

        if self.debugMode:
            try:
                print(json.dumps(response.json(), indent=4))
            except:
                print("Empty response")

        return response

    def delete(self, path, params={}):
        # TODO: Implement delete method
        pass