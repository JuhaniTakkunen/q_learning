from typing import List, Optional
import random

try:
    from firm import Firm
except ImportError:
    # ImportError: cannot import name 'Firm' from partially initialized module 'firm' (most likely due to a circular import)
    pass

from cournot import Cournot
from competition import OMEGA, LAMBDA, THETA


import logging
logger = logging.getLogger(__name__)


class QLearning:

    def __init__(self, seed, sim_manager):
        logger.debug("Start initializing this: %s", self.__class__)

        self.q: List[List[float]] = []

        # self.bertrand: Bertrand = None
        self.SimulationManager = sim_manager
        self.seed = seed
        self.cournot: Cournot = None
        self.epsilon = 1.0
        self.numberOfEpisodes = 0

        self.sizeOfActionSet: int = sim_manager.sizeOfActionSet
        self.alpha: float = sim_manager.alpha
        self.delta: float = sim_manager.delta
        self.beta: float = sim_manager.beta
        self.gamma: float = sim_manager.gamma

        random.seed(seed)
        self.initialize()
        logger.debug("Init completed: %s", self.__class__)


    def initialize(self):

        # instantiate competition class
        if self.SimulationManager.competition == "bertrand":
            raise NotImplementedError("Didnt bother")
        elif self.SimulationManager.competition == "cournot":
            self.cournot = Cournot()

        # initialize Q-matrix
        self.q = [[None]*self.sizeOfActionSet] * self.sizeOfActionSet

        for i in range(self.sizeOfActionSet):
            logger.debug("looping i: %s / %s", i, self.sizeOfActionSet)
            for j in range(self.sizeOfActionSet):

                total = 0
                if self.SimulationManager.competition == "bertrand":
                    raise NotImplementedError("Didnt bother")
                elif self.SimulationManager.competition == "cournot":
                    for k in range(self.sizeOfActionSet):
                        if self.SimulationManager.marketSize == 2:
                            price = self.cournot.calculatePriceDuo(j, k)
                            total += self.cournot.calculateProfitDuo(price, j)
                        if self.SimulationManager.marketSize == 3:
                            for l in range(self.sizeOfActionSet):
                                price = self.cournot.calculatePriceTrio(j, k, l)
                                total += self.cournot.calculateProfitTrio(price, j)
                self.q[i][j] = total / (self.sizeOfActionSet ** (self.SimulationManager.marketSize - 1))


    def episode(self, other_firm_1, other_firm_2: Optional = None) -> int:

        if not other_firm_2:

            if self.SimulationManager.competition_type == "bertrand":
                raise NotImplementedError("Didnt bother")
            elif self.SimulationManager.competition_type == "cournot":
                state = int(other_firm_1.get_quantity())
                action = self.selectAction(state)

                price = self.cournot.calculatePriceDuo(action, state)
                reward = self.cournot.calculateProfitDuo(price, action)
            else:
                raise ValueError(f"Invalid competition type: {self.SimulationManager.competition_type}")

        else:
            if self.SimulationManager.competition_type == "bertrand":
                raise NotImplementedError("Didnt bother")
            elif self.SimulationManager.competition_type == "cournot":
                stateOtherFirm1 = round(other_firm_1.get_quantity())
                stateOtherFirm2 = round(other_firm_2.get_quantity())
            else:
                raise ValueError(
                    f"Invalid competition type: {self.SimulationManager.competition_type}")
            if stateOtherFirm1 < stateOtherFirm2:
                state = round((self.gamma * stateOtherFirm1 + (1 - self.gamma) * stateOtherFirm2) / 2)
            elif stateOtherFirm1 > stateOtherFirm2:
                lol = (1 - self.gamma) * stateOtherFirm1 + self.gamma * stateOtherFirm2
                state = round(lol / 2)
            else:
                state = round((stateOtherFirm1 + stateOtherFirm2) / 2)

            action = self.selectAction(state)

            if self.SimulationManager.competition_type == "bertrand":
                raise NotImplementedError("Didnt bother")
            elif self.SimulationManager.competition_type == "cournot":
                price = self.cournot.calculatePriceTrio(action, stateOtherFirm1, stateOtherFirm2)
                reward = self.cournot.calculateProfitTrio(price, action)
            else:
                raise ValueError(
                    f"Invalid competition type: {self.SimulationManager.competition_type}")

        nextMaxQ = self.valueAtIndex(action, self.getMaxActionIndex(action))

        try:
            temp1 = (1 - self.alpha) * self.q[state][action]
            temp2 = self.alpha * (reward + self.delta * nextMaxQ)
            self.q[state][action] = temp1 + temp2
        except Exception:
            logger.error(other_firm_1)
            logger.error(other_firm_2)
            logger.error(state)
            logger.error(action)
            logger.error(len(self.q))
            raise

        self.numberOfEpisodes += 1
        self.epsilon = (1 - self.beta) ** self.numberOfEpisodes
        return action

    def selectAction(self, state: int) -> int:
        if random.random() > self.epsilon:
            # exploit
            return self.getMaxActionIndex(state)
        else:
            # explore
            return random.randint(0, self.sizeOfActionSet - 1)  # I think -1 is needed. -JT-

    def getMaxActionIndex(self, state: int) -> int:
        row = self.q[state]
        return row.index(max(row))

    def valueAtIndex(self, state, action) -> float:
        return self.q[state][action]

