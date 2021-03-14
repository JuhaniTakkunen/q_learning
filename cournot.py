from competition import OMEGA, LAMBDA, THETA

coeffProfitDuoCournot = 1.0
coeffProfitTrioCournot = 1.5625
coeffQDuoCournot = (60.0 / 100.0)
coeffQTrioCournot = (300.0 / 700.0)


# DUOPOLY
class Cournot:

    @staticmethod
    def calculatePriceDuo(q: float, qOtherFirm: float) -> float:
        q = q * coeffQDuoCournot
        qOtherFirm = qOtherFirm * coeffQDuoCournot

        return OMEGA - LAMBDA * (q + THETA * qOtherFirm)

    @staticmethod
    def calculateProfitDuo(p: float, q: float) -> float:
        return p * q * coeffProfitDuoCournot


    # TRIOPOLY
    @staticmethod
    def calculatePriceTrio(q: float, qOtherFirm1: float, qOtherFirm2: float) -> float:
        q = q * coeffQTrioCournot
        qOtherFirm1 = qOtherFirm1 * coeffQTrioCournot
        qOtherFirm2 = qOtherFirm2 * coeffQTrioCournot

        return OMEGA - LAMBDA * (q + THETA * (qOtherFirm1 + qOtherFirm2))

    @staticmethod
    def calculateProfitTrio(p: float, q: float) -> float:
        return p * q * coeffProfitTrioCournot
