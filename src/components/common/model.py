class Model:

    def __init__(self, name: str, version: int, sla: int):
        self.name = name
        self.version = version
        self.sla = sla

    def to_json(self):
        return {
            "name": self.name,
            "version": self.version,
            "sla": self.sla
        }