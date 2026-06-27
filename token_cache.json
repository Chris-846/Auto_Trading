import json
import requests

def maketoken(dist = "REAL"):

    global stock_info
    
    headers = {"content-type":"application/json"}
    body = {
        "grant_type":"client_credentials",
        "appkey":stock_info['REAL_APP_KEY'], 
        "appsecret":stock_info['REAL_APP_SECRET']
        }

    # 한국투자증권에 Request
    PATH = "oauth2/tokenP"
    URL = f"{stock_info['REAL_URL']}/{PATH}"
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

{"date": "2024-06-18", "access_token": "", "expires_in": 3600}
