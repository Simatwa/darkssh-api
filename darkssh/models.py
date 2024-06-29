from pydantic import BaseModel, IPvAnyAddress
from datetime import datetime

class SlowDNS(BaseModel):
        """
        ```json
        {
                "dns": "1.1.1.1",
                "ns": "ns-us.servergo.pw",
                "pubkey": "0c636786a0f668eea5e188959a9f350694bb2f4fc1ed4b8e2e690d26f217481a",
                "domain": "sl.us.servergo.pw",
                "port": "443, 80, 53, 5300"
        }
        ```
        """
        dns : IPvAnyAddress
        ns : str
        pubkey : str
        domain : str
        port : str
    

class Data1(BaseModel):
        """
        ```json
        {
            "payload_http": "GET / HTTP/1.1[crlf]Host: us.servergo.pw[crlf]Connection: Upgrade[crlf]User-Agent: [ua][crlf]Upgrade: websocket[crlf][crlf]",
            "payload_https": "GET wss://bug.com/ HTTP/1.1[crlf]Host: us.servergo.pw[crlf]Connection: Upgrade[crlf]User-Agent: [ua][crlf]Upgrade: websocket[crlf][crlf]",
            "username": "darkssh_smartwalajja",
            "password": "12441244",
            "ip": "172.105.154.151",
            "host": "ssh.us.servergo.pw",
            "exp": "2024-07-30T00:58",
            "slowdns": `SlowDNS`,
            "credits": "lionssh Dev"
        }
        ```
        """
        payload_http : str
        payload_https : str
        username : str
        password: str
        ip : IPvAnyAddress
        host : str
        exp : datetime
        slowdns: SlowDNS
        credits: str|None=None

class Data(BaseModel):
        """
        ```json
    {
        "level": "success",
        "ip": "a.us.servergo.pw",
        "username": "darkssh_smartwalajja",
        "password": "12441244",
        "dp": "80, 443",
        "op": "22, 4 44",
        "ssl": "80, 443",
        "squid": "8080, 1080",
        "exp": "2024-07-30",
        "data": `Data1`
    }
        ```
    """
        level : str
        ip : str
        username : str
        password : str
        dp: str
        op : str
        ssl : str
        squid : str
        exp : datetime
        data: Data1

class SSHModel(BaseModel):
    """
    ```json
    {
        "success": true,
        "data" : `Data`
    }
    ```
    """
    success : bool
    data  : Data