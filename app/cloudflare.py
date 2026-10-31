import json
import re
import sys

import requests
from termcolor import colored, cprint


def getZoneId(token, domain):
    url = "https://api.cloudflare.com/client/v4/zones"
    payload={}
    headers = {
    'Authorization': f"Bearer {token}"
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    if data['success']:
        for zone in data['result']:
            if zone['name'] == domain:
                return zone['id']
        raise ValueError(f"Cloudflare zone not found for domain: {domain}")
    else:
        sys.exit(colored('getZoneId(): '+json.dumps(data['errors'], indent=2), "red"))


def getZoneRecords(token, domain, hostname=False, zoneId: str | None = None):
    if not zoneId:
        zoneId = getZoneId(token, domain)
    url = f"https://api.cloudflare.com/client/v4/zones/{zoneId}/dns_records?per_page=150"
    payload={}
    headers = {
    'Authorization': f"Bearer {token}"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    output = []

    if data['success']:
        for record in data['result']:
            if record['type'] in ['A', 'AAAA']:
                #print("{name} {ttl} in {type} {content}".format(name=record['name'], ttl=record['ttl'], type=record['type'], content=record['content']))
                output.append(record)
        return output
    else:
        sys.exit(colored("getZoneRecords() - error\n{}".format(json.dumps(data['errors'], indent=2)), "red"))

def createDNSRecord(token, domain, name, type, content, subdomain=None, zoneId=False, priority=False, ttl=120):
    if zoneId != False:
        url = f"https://api.cloudflare.com/client/v4/zones/{zoneId}/dns_records"
    else:
        url = f"https://api.cloudflare.com/client/v4/zones/{getZoneId(token, domain)}/dns_records"
    if subdomain:
        fqdn = name+"."+subdomain+"."+domain
    else:
        fqdn = name+"."+domain

    payload={
        'type': type,
        'name': fqdn,
        'content': content,
        'ttl': ttl
    }
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    data = json.loads(response.text)

    if data['success'] == True:
        print("--> [CLOUDFLARE] [{code}] {msg}".format(code=response.status_code, msg=colored('record created', "green")))
        return True
    else:
        cprint("[ERROR]", 'red')
        sys.exit("createDNSRecord():  "+json.dumps(data['errors'], indent=2))

def deleteDNSRecord(token, domain, id, zoneId=False):
    if zoneId != False:
        url = f"https://api.cloudflare.com/client/v4/zones/{zoneId}/dns_records/{id}"
    else:
        url = f"https://api.cloudflare.com/client/v4/zones/{getZoneId(token, domain)}/dns_records/{id}"
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.request("DELETE", url, headers=headers)
    data = json.loads(response.text)
    print("--> [CLOUDFLARE] [{code}] {msg}".format(code=response.status_code, msg=colored('record deleted', "green")))

def isValidDNSRecord(name):
    regex = r"^([a-zA-Z]|\d|-|\.)*$"
    return re.match(regex, name)



if __name__ == '__main__':
    token = ""
    domain = ""
    print(getZoneId(token, domain))
    print(json.dumps(getZoneRecords(token, domain), indent=2))
