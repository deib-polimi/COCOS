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


class CTController(Controller):
    BC = 0.21
    DC = 0.2

    def update(self, users, rt):
        e = self.v_sla - 1/rt
        xc = float(self.xc_prec + self.BC * e)
        self.nc = max(1, xc + self.DC * e)
        self.xc_prec = float(self.nc - self.BC * e)
        return self.nc
