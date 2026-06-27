import json
import requests
import Config from config

def maketoken(dist = "REAL"):

    
    
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
        "appkey":stock_info[config.app_key], 
        "appsecret":stock_info[config.app_secret] }

    # 한국투자증권에 Request
    PATH = "oauth2/tokenP"
    URL = f"{stock_info[config.api_domain]}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    
    if res.status_code == 200:
        my_token = res.json()["access_token"]

        datadict = dict()

        # 해당 토큰을 작업 공간에 저장
        datadict["authorization"] = my_token
        with open('./stock_token.json', 'w') as outfile:
            json.dump(datadict, outfile)   

        print("My TOKEN : ", my_token)
        return my_token

    else:
        raise Exception('status code not 200 & Token Auth Fail!')
