import configparser
import os
from sys import exit

from termcolor import cprint

keysToImport = ['cf-key', 'cf-domain', 'ts-tailnet']
keysOptional = ['cf-sub', 'prefix', 'postfix', 'ts-key', 'ts-client-id', 'ts-client-secret', "mode", "hs-baseurl", "hs-apikey"]

def importkey(name, optional=False):
    key = name
    envKey = key.replace("-", "_")

    secretPath = "/run/secrets/"+key
    if os.path.isfile(secretPath):
        with open(secretPath, "r", encoding="utf-8") as secret:
            return secret.readline().strip()
    if (key in os.environ):
        return os.environ.get(key)
    if (envKey in os.environ):
        return os.environ.get(envKey)

    cfgPath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
    try:
        with open(cfgPath, 'r') as file:
            config = configparser.ConfigParser()
            config.read_file(file)
            return config['DEFAULT'][key]
    except (OSError, configparser.Error, KeyError) as e:
        print(e)
        if optional:
            return ""
        cprint(f"ERROR: mandatory configuration not found: {key}", "red")
        exit('could not read config file')


def getConfig():
    # static = {
    #     'cf-key': '',
    #     'cf-domain': "".lower(),
    #     'ts-key': 'tskey-',
    #     'ts-tailnet': ''
    # }
    static = {}

    for key in keysToImport:
        static[key] = importkey(key)
    for key in keysOptional:
        static[key] = importkey(key, True)

    # check for tailscale config
    if static['mode'] == "" or static['mode'] == "tailscale":
        static['mode'] = "tailscale"
        if not static['ts-key'] and not (static['ts-client-id'] and static['ts-client-secret']):
            cprint("ERROR: mandatory tailscale configuration not found: ts-key or ts-client-id/ts-client-secret missing", "red")
            exit(1)
    # check for headscale Config
    if static['mode'] == "headscale" and not (static['hs-baseurl'] and static['hs-apikey']):
            cprint("ERROR: mandatory headscale configuration not found: hs-baseurl and/or hs-apikey missing", "red")
            exit(1)
    # unkown mode unfigured
    if static['mode'] not in ["", "tailscale", "headscale"]:
        cprint("ERROR: unknown mode configured (got: {mode})".format(mode=static['mode']), "red")
        exit(1)

    return static

if __name__ == '__main__':
    from pprint import pprint
    pprint(getConfig())
