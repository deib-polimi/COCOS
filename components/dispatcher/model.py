import uuid


class Model:
    def __init__(self,
                 model: str,
                 version: int,
                 active: bool = False,
                 device=None,
                 node: str = None,
                 endpoint: str = None,
                 port: int = None,
                 quota: float = None) -> None:
        self.id = uuid.uuid4()
        self.model = model
        self.version = version
        self.active = active

        self.device = device
        self.node = node
        self.endpoint = endpoint
        self.port = port
        self.quota = quota

    def to_json(self):
        return {
            "id": self.id,
            "model": self.model,
            "version": self.version,
            "active": self.active,
            "device": self.device,
            "node": self.node,
            "endpoint": self.endpoint,
            "port": self.port,
            "quota": self.quota
        }


class Device:
    CPU = 0
    GPU = 1
