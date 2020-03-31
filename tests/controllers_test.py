from components.controller import CTController


class Application:
    A1_NOM = 0.00763
    A2_NOM = 0.0018
    A3_NOM = 0.5658

    def __init__(self, sla):
        self.cores = 1
        self.RT = 0.0
        self.sla = sla

    def setRT(self, req):
        exactRT = self.__computeRT__(req)
        self.RT = exactRT  # * (1.0+random.random()/10)
        return self.RT

    def __computeRT__(self, req):
        return ((1000.0*self.A2_NOM+self.A1_NOM)*req+1000*self.A1_NOM*self.A3_NOM*self.cores)/(req+1000.0*self.A3_NOM*self.cores)


a = Application(0.6)


def test_small_ramp():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(i, a.setRT(i)) <= 1


def test_big_ramp():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(100, 1000, 10):
        assert controller.update(i, a.setRT(i)) < 20


def test_step0():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(100, a.setRT(100)) <= 1
    for i in range(1, 100):
        assert controller.update(500, a.setRT(500)) < 20


def test_step1():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(100, a.setRT(100)) <= 1
    for i in range(1, 100):
        assert controller.update(600, a.setRT(600)) < 20


def test_step2():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(200, a.setRT(200)) <= 1
    for i in range(1, 100):
        assert controller.update(700, a.setRT(700)) < 20


def test_step3():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(300, a.setRT(300)) <= 3
    for i in range(1, 100):
        assert controller.update(800, a.setRT(800)) < 20


def test_step4():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(100, a.setRT(100)) <= 1
    for i in range(1, 100):
        assert controller.update(800, a.setRT(800)) < 20


def test_step5():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(200, a.setRT(200)) <= 200
    for i in range(1, 100):
        assert controller.update(900, a.setRT(900)) < 20


def test_step6():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(1, 100):
        assert controller.update(100, a.setRT(100)) <= 1
    for i in range(1, 100):
        assert controller.update(1000, a.setRT(1000)) < 20


def test_constant():
    controller = CTController(None)
    controller.v_sla = 1 / a.sla
    for i in range(100, 500, 10):
        assert controller.update(i, a.setRT(i)) <= 10
    for i in range(100, 500, 10):
        assert controller.update(500, a.setRT(500)) <= 10
