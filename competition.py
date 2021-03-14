
OMEGA = 100
LAMBDA = 1.0
THETA = (2/3)


def calc_omega(n: float) -> float:
    return OMEGA / (LAMBDA * (1 + (n - 1) * THETA))


def calc_lambda(n: float) -> float:
    return (1 + (n - 2) * THETA) / (LAMBDA * (1 - THETA) * (1 + (n - 1) * THETA))


def calc_theta(n: float) -> float:
    return ((n - 1) * THETA) / (LAMBDA * (1 - THETA) * (1 + (n - 1) * THETA))

