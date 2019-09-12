import logging


class Actuator:

    def __init__(self, client):
        self.client = client
        self.containers = None

    def init(self):
        self.containers = [{"id": container.attrs["Id"],
                            "image": container.attrs["Config"]["Image"],
                            "name": container.attrs["Name"],
                            "status": container.attrs["State"]["Status"],
                            "container_name": container.attrs["Config"]["Labels"]["io.kubernetes.container.name"]}
                           for container in self.client.containers.list()]
        logging.info("Found %d containers: %s", len(self.containers), self.containers)
        return self.containers

    def set_quota(self, container_id: str, cpu_quota: int):
        logging.info("Setting %f quota to %s", cpu_quota, container_id)

        container = self.client.containers.get(container_id)
        resp = container.update(cpu_quota=cpu_quota)

        return resp
