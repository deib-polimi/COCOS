class Model:

    def __init__(self, name: str = None, version: int = None, sla: int = None, json_data=None):
        if json_data:
            self.__dict__ = json_data
        else:
            self.name = name
            self.version = version
            self.sla = sla

    def to_json(self):
        return {
            "name": self.name,
            "version": self.version,
            "sla": self.sla
        }
