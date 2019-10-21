class Model:

    def __init__(self,
                 name: str = None,
                 version: int = None,
                 sla: float = None,
                 alpha: float = 1,
                 json_data=None):
        if json_data:
            self.__dict__ = json_data
        else:
            self.name = name
            self.version = version
            self.sla = sla
            self.alpha = alpha

    def to_json(self):
        return {
            "name": self.name,
            "version": self.version,
            "sla": self.sla,
            "alpha": self.alpha
        }
