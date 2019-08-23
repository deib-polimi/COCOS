class Container:
    def __init__(self,
                 model: str,
                 version: int,
                 active: bool = False,
                 container: str = None,
                 node: str = None,
                 port: int = None,
                 device=None,
                 quota: float = None) -> None:
        self.model = model
        self.version = version
        self.active = active

        self.container = container
        self.node = node
        self.port = port
        self.device = device
        self.endpoint = "http://" + node + ":" + str(port)
        self.quota = quota

        self.container_id = None

    def __str__(self):
        return 'c: {} m: {} v: {}'.format(str(self.container), self.model, self.version)

    def to_json(self):
        return {
            "model": self.model,
            "version": self.version,
            "container": self.container,
            "container_id": self.container_id,
            "active": self.active,
            "device": self.device,
            "node": self.node,
            "endpoint": self.endpoint,
            "port": self.port,
            "quota": self.quota
        }