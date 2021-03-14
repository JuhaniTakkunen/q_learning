from cournot import Cournot
from q_learning import QLearning


import logging
logger = logging.getLogger(__name__)


class Firm:

    def __init__(self, simulation_run, seed: int):
        logger.info("Start initializing this: %s", self.__class__)
        self.SimulationManager = simulation_run.SimulationManager
        self.price = 0.0
        self.quantity = 0.0
        self.profit = 0.0
        self.qlearning = QLearning(seed, self.SimulationManager)                # holds the firm's individual Q-learning algorithm
        self.simulationRun = simulation_run        # holds the simulation run it belongs to
        # ArrayLists to store its parameters over the time
        self.prices = []
        self.quantities = []
        self.profits = []
        logger.info("Init completed: %s", self.__class__)


    def getQuantity(self):
        logger.debug(DeprecationWarning("This should not be used"))
        return self.get_quantity()

    def getState(self):
        logger.debug(DeprecationWarning("This should not be used"))
        return self.get_state()

    def getPrice(self):
        logger.debug(DeprecationWarning("This should not be used"))
        return self.get_price()

    def get_state(self):

        if self.SimulationManager.competition_type == "bertrand":
            return self.price
        if self.SimulationManager.competition_type == "cournot":
            return self.quantity
        return 0.0

    def run_episode(self) -> float:

        # get all competitors
        known_firms = [self]
        other_firm_1 = self.simulationRun.getOtherFirm(known_firms)
        known_firms.append(other_firm_1)

        # call Q-Learning
        if self.SimulationManager.marketSize == 2:
            return self.qlearning.episode(other_firm_1)
        if self.SimulationManager.marketSize == 3:
            other_firm_2 = self.simulationRun.getOtherFirm(known_firms)
            return self.qlearning.episode(other_firm_1, other_firm_2)
        return 0

    def set_state(self, state: float):
        if self.SimulationManager.competition_type == "bertrand":
            self.price = state
        if self.SimulationManager.competition_type == "cournot":
            self.quantity = state

    def calculate_firm_data(self):

        # get all competitors
        known_firms = [self]
        other_firm_1 = self.simulationRun.getOtherFirm(known_firms)
        known_firms.append(other_firm_1)


        # calculate data corresponding to the states set
        if self.SimulationManager.competition_type == "bertrand":
            raise NotImplementedError("do if you wanna")
        if self.SimulationManager.competition_type == "cournot":
            cournot = Cournot()
            state_other_firm_1 = other_firm_1.get_quantity()

            if self.SimulationManager.marketSize == 2:
                self.price = cournot.calculatePriceDuo(self.quantity, state_other_firm_1)
                self.profit = cournot.calculateProfitDuo(self.price, self.quantity)
            if self.SimulationManager.marketSize == 3:
                other_firm_2 = self.simulationRun.getOtherFirm(known_firms)
                state_other_firm_2 = other_firm_2.get_quantity()

                self.price = cournot.calculatePriceTrio(self.quantity, state_other_firm_1, state_other_firm_2)
                self.profit = cournot.calculateProfitTrio(self.price, self.quantity)

        # add data to ArrayList for export and examination purposes
        self.prices.append(self.price)
        self.quantities.append(self.quantity)
        self.profits.append(self.profit)

        # if ArrayLists hold more than the intended entries, the oldest ones get removed
        if len(self.prices) > self.SimulationManager.sizeOfExaminationInterval:
            self.prices.pop(0)
            self.quantities.pop(0)
            self.profits.pop(0)

    def check_if_last_periods_are_identical(self) -> bool:
        if len(self.prices) > 1 or len(self.quantities) > 1:

            if self.SimulationManager.competition_type == "bertrand":
                raise NotImplementedError("Didnt bother")

            elif self.SimulationManager.competition_type == "cournot":
                if abs(self.quantities[-1] - self.quantities[-2]) < 0.01:
                    # print("difference less than 0.01")
                    return True

            else:
                raise ValueError(f"what type is this?? {self.SimulationManager.competition_type}")
        return False

    def get_price(self) -> float:
        return round(self.price, ndigits=2)

    def get_quantity(self) -> float:
        return round(self.quantity, ndigits=2)
