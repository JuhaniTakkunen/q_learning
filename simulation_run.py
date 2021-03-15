import logging
import random
from typing import List

from calculation import get_mean, get_sd
from firm import Firm


logger = logging.getLogger(__name__)


class SimulationRun:

    def __init__(self, seed, sim_manager):
        logger.debug("Start initializing this: %s", self.__class__)
        self.firm = []
        self.numberOfPeriods = 0
        self.numberOfConvergedPeriods = 0
        self.SimulationManager = sim_manager
        self.market_size = sim_manager.marketSize

        for x in range(self.market_size):
            self.firm.append(Firm(self, x))

        random.seed(seed)
        logger.debug("init completed: %s", self.__class__)

    def simulate(self):

        if self.SimulationManager.marketTiming == "discrete":
            func = self._simulate_discrete
        elif self.SimulationManager.marketTiming == "random":
            func = self._simulate_random
        else:
            logger.error(self.SimulationManager.marketTiming)
            raise ValueError("wut?")

        while self.numberOfPeriods < self.SimulationManager.maxNumberOfPeriods and self.numberOfConvergedPeriods < self.SimulationManager.minNumberOfConvergedPeriods:
            state = func()
            [f.set_state(s) for s, f in zip(state, self.firm)]
            [x.calculate_firm_data() for x in self.firm]

            self.comparePeriods()
            self.numberOfPeriods += 1

    def _simulate_discrete(self):

        if self.numberOfPeriods % self.SimulationManager.updateInterval == 0:
            state = [x.run_episode() for x in self.firm]
        else:
            state = [x.get_state() for x in self.firm]
        return state

    def _simulate_random(self):
        state = [x.get_state() for x in self.firm]
        randomFirm = random.randint(0, self.market_size - 1)  # I think -1 is needed. -JT-
        state[randomFirm] = self.firm[randomFirm].run_episode()
        return state

    def comparePeriods(self):
        for x in self.firm:
            if not x.check_if_last_periods_are_identical():
                self.numberOfConvergedPeriods = 0
                return
        self.numberOfConvergedPeriods += 1

    def getOtherFirm(self, known_firms: List[Firm]):
        for x in self.firm:
            if x not in known_firms:
                return x
        return None

    def getMeanPrice(self):
        all_values = []
        for x in self.firm:
            all_values.extend(x.get_prices())
        return round(get_mean(all_values), ndigits=2)

    def getSDPrice(self):
        all_values = []
        for x in self.firm:
            all_values.extend(x.get_prices())
        return round(get_sd(all_values), ndigits=2)

    def getMeanQuantity(self):
        all_values = []
        for x in self.firm:
            all_values.extend(x.get_quantities())
        return round(get_mean(all_values), ndigits=2)

    def getMeanProfit(self):
        all_values = []
        for x in self.firm:
            all_values.extend(x.get_profits())
        return round(get_mean(all_values), ndigits=2)

    def getNumberOfPeriods(self):
        return self.numberOfPeriods

    def getDegreeOfTacitCollusion(self) -> float:
        price = self.getMeanPrice()
        nash = 0.0
        jpm = 50.0

        if self.SimulationManager.competition == "cournot":
            if self.market_size == 2:
                nash = 37.5
            if self.market_size == 3:
                nash = 30.0
        if self.SimulationManager.competition == "bertrand":
            raise NotImplementedError("en pysty")

        return round((price - nash) / (jpm - nash), 3)