from .container import Container


class Controller:
    def __init__(self, container: Container):
        self.v_sla = 0
        self.v_gpu = 0
        self.v_cpu = 0
        self.v_o_cpu = 0
        self.gpu_over_performing = False
        self.e = 0
        self.xc = 0
        self.xc_prec = 0
        self.nc = 0

        self.container = container

    def to_json(self):
        return {
            "v_sla": self.v_sla,
            "v_gpu": self.v_gpu,
            "v_cpu": self.v_cpu,
            "v_o_cpu": self.v_o_cpu,
            "gpu_over_performing": self.gpu_over_performing,
            "e": self.e,
            "xc": self.xc,
            "xc_prec": self.xc_prec,
            "nc": self.nc,
            "container": self.container.to_json()
        }
