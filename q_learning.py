from functools import lru_cache
from math import floor
from typing import List, Optional
import random
import numpy as np

try:
    from firm import Firm
except ImportError:
    # ImportError: cannot import name 'Firm' from partially initialized module 'firm' (most likely due to a circular import)
    pass

from cournot import Cournot
from competition import OMEGA, LAMBDA, THETA


import logging
logger = logging.getLogger(__name__)


@lru_cache(8)
def _initial_array(competition_type, size_of_action_set, market_size):
    cournot = Cournot()
    if competition_type == "bertrand":
        raise NotImplementedError("Didnt bother")

    # initialize Q-matrix
    q = np.empty([size_of_action_set, size_of_action_set])

    for i in range(size_of_action_set):
        logger.debug("looping i: %s / %s", i, size_of_action_set)

        for j in range(size_of_action_set):

            total = 0

            for k in range(size_of_action_set):
                if market_size == 2:
                    price = cournot.calculatePriceDuo(j, k)
                    total += cournot.calculateProfitDuo(price, j)
                if market_size == 3:
                    for l in range(market_size):
                        price = cournot.calculatePriceTrio(j, k, l)
                        total += cournot.calculateProfitTrio(price, j)
            q[i][j] = total / (size_of_action_set ** (market_size - 1))
    return q

class QLearning:

    def __init__(self, seed, sim_manager):
        logger.debug("Start initializing this: %s", self.__class__)

        self.q: np.array = None

        # self.bertrand: Bertrand = None
        self.market_size = sim_manager.marketSize
        self.competition_type = sim_manager.competition
        
        self.seed = seed
        self.cournot: Cournot = Cournot()
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

        # instantiate competition class
        if self.competition_type == "bertrand":
            raise NotImplementedError("Didnt bother")
        elif self.competition_type == "cournot":
            pass
        else:
            raise ValueError("invalid competition type")

    def initialize(self):
        new_array = _initial_array(
            competition_type=self.competition_type,
            size_of_action_set=self.sizeOfActionSet,
            market_size=self.market_size)
        self.q = np.copy(new_array)

    def episode_companies_2(self, other_firm_1) -> int:

        if self.competition_type == "bertrand":
            raise NotImplementedError("Didnt bother")
        elif self.competition_type == "cournot":
            state = floor(other_firm_1.get_quantity())
            action = self.selectAction(state)

            price = self.cournot.calculatePriceDuo(action, state)
            reward = self.cournot.calculateProfitDuo(price, action)
        else:
            raise ValueError(f"Invalid competition type: {self.competition_type}")

        return self._episode_calc(action, state, reward)

    def episode_companies_3(self, other_firm_1, other_firm_2) -> int:

        if self.competition_type == "bertrand":
            raise NotImplementedError("Didnt bother")
        elif self.competition_type == "cournot":
            stateOtherFirm1 = floor(other_firm_1.quantity)
            stateOtherFirm2 = floor(other_firm_2.quantity)
        else:
            raise ValueError(
                f"Invalid competition type: {self.competition_type}")
        if stateOtherFirm1 < stateOtherFirm2:
            state = round((self.gamma * stateOtherFirm1 + (1 - self.gamma) * stateOtherFirm2) / 2)
        elif stateOtherFirm1 > stateOtherFirm2:
            state = round(((1 - self.gamma) * stateOtherFirm1 + self.gamma * stateOtherFirm2) / 2)
        else:
            state = round((stateOtherFirm1 + stateOtherFirm2) / 2)

        action = self.selectAction(state)

        if self.competition_type == "bertrand":
            raise NotImplementedError("Didnt bother")
        elif self.competition_type == "cournot":
            price = self.cournot.calculatePriceTrio(action, stateOtherFirm1, stateOtherFirm2)
            reward = self.cournot.calculateProfitTrio(price, action)
        else:
            raise ValueError(
                f"Invalid competition type: {self.competition_type}")

        return self._episode_calc(action, state, reward)

    def _episode_calc(self, action, state, reward) -> int:
        # nextMaxQ = self.valueAtIndex(
        #     state=action,
        #     action=self.getMaxActionIndex(action))

        next_max_q = self.q[action].max()  # NOTE: Should this be state?

        temp1 = (1 - self.alpha) * self.q[state][action]
        temp2 = self.alpha * (reward + self.delta * next_max_q)
        self.q[state][action] = temp1 + temp2

        self.numberOfEpisodes += 1
        self.epsilon = (1 - self.beta) ** self.numberOfEpisodes
        return action

    def selectAction(self, state: int) -> int:
        if random.random() > self.epsilon:
            # exploit
            return self.getMaxActionIndex(state)
        else:
            # explore
            return random.randint(0, self.sizeOfActionSet - 1)

    def getMaxActionIndex(self, state: int) -> int:
        # row = self.q[state]
        # return row.index(max(row))
        return self.q[state].argmax()

    def valueAtIndex(self, state, action) -> float:
        return self.q[state][action]

