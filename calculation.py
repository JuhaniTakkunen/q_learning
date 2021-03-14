from statistics import mean, stdev


def get_mean(data) -> float:
    new_mean = mean(data)
    return round(new_mean, ndigits=3)


def get_sd(data) -> float:
    new_mean = stdev(data)
    return round(new_mean, ndigits=3)
