import ipaddress
import json
import sys

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from termcolor import colored


### Get Data
def getTailscaleDevice(apikey, clientid, clientsecret, tailnet):
    if clientid and clientsecret:
        token = OAuth2Session(client=BackendApplicationClient(client_id=clientid)).fetch_token(token_url='https://api.tailscale.com/api/v2/oauth/token', client_id=clientid, client_secret=clientsecret)
        apikey = token["access_token"]
    url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
    payload={}
    headers = {
    }
    response = requests.request("GET", url, headers=headers, data=payload, auth=HTTPBasicAuth(username=apikey, password=""))
    # print(response.text)
    # print(json.dumps(json.loads(response.text), indent=2))

    output=[]

    data = json.loads(response.text)
    if (response.status_code == 200):
        output = []
        for device in data['devices']:
            #print(device['hostname']+": "+json.dumps(device['addresses']))
            for address in device['addresses']:
                output.append({'hostname': alterHostname(device['hostname']), 'address': address})
                if device['name'].split('.')[0].lower() != device['hostname'].lower():
                    output.append({'hostname': alterHostname(device['name'].split('.')[0].lower()), 'address': address})
        return output
    else:
        sys.exit(colored("getTailscaleDevice() - {status}, {error}".format(status=str(response.status_code), error=data['message']), "red"))

def isTailscaleIP(ip):
    ip = ipaddress.ip_address(ip)

    if (ip.version == 6):
        return ip in ipaddress.IPv6Network('fd7a:115c:a1e0::/48')
    elif (ip.version == 4):
        return ip in ipaddress.IPv4Network('100.64.0.0/10')
    else:
        sys.exit("isTailscaleIP(): - unknown IP version")

def alterHostname(hostname):
    from config import getConfig
    config = getConfig()
    pre = config.get("prefix", "")
    post = config.get("postfix", "")

    newHostname = f"{pre}{hostname}{post}"
    return newHostname

if __name__ == '__main__':
    print(json.dumps(getTailscaleDevice(), indent=2))
