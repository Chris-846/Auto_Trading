import json
import requests

def maketoken(config, dist="REAL"):
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": config.app_key,
        "appsecret": config.app_secret
    }

    PATH = "oauth2/tokenP"
    URL = f"{config.api_domain}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))

    if res.status_code == 200:
        my_token = res.json().get("access_token")

        datadict = {"authorization": my_token}
        with open('./stock_token.json', 'w') as outfile:
            json.dump(datadict, outfile)

        print("My TOKEN:", my_token)
        return my_token
    else:
        raise Exception('status code not 200 & Token Auth Fail!')
