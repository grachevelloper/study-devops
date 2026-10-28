from pathlib import Path

import grpc

from . import api_pb2, api_pb2_grpc


class Certs:
    def __init__(self, root, cert, key):
        self.root = Path(root).read_bytes()
        self.cert = Path(cert).read_bytes()
        self.key = Path(key).read_bytes()


class Client:
    def __init__(self, addr: str, crt: Certs):
        creds = grpc.ssl_channel_credentials(crt.root, crt.key, crt.cert)
        self.channel = grpc.secure_channel(addr, creds)
        self.rpc = api_pb2_grpc.DiceServiceStub(self.channel)

    def roll_die(self) -> int:
        try:
            return self.rpc.RollDie(api_pb2.RollDieRequest(), timeout=5).value
        finally:
            self.channel.close()
