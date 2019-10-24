class Container:
    def __init__(self,
                 model: str = None,
                 version: int = None,
                 active: bool = False,
                 container: str = None,
                 node: str = None,
                 port: int = None,
                 device: int = None,
                 quota: float = None,
                 json_data=None) -> None:
        if json_data:
            self.__dict__ = json_data
        else:
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
        return 'C: {}, M: {}/V{}'.format(str(self.container), self.model, self.version)

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
