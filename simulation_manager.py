import logging
import math
from datetime import datetime
from typing import List

from calculation import get_mean, get_sd
from simulation_run import SimulationRun

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.info("Start program")
logger.debug("logging level set to debug")

class SimulationManager:
    def __init__(self):
        # input parameters
        self.marketTiming = "discrete"
        self.competition = "cournot"
        self.competition_type = self.competition
        self.marketSize = 3

        # simulation settings
        self.numberOfSimulationRuns = None
        self.sizeOfActionSet = 101
        self.updateInterval = 1
        self.maxNumberOfPeriods = self.sizeOfActionSet * self.sizeOfActionSet * 5000
        self.minNumberOfConvergedPeriods = 100 * self.updateInterval
        self.sizeOfExaminationInterval = 100 * self.updateInterval

        # q-learning
        self.alpha = None
        self.delta = None
        self.beta = 0.000000270865
        self.gamma = None

        # store results
        self.prices = []
        self.pricesSD = []
        self.quantities = []
        self.profits = []
        self.degrees = []
        self.periods = []

        # Starting time of the simulation
        self.startingTime = None
        self.startingTimeInMillis = None
        self.dtf = None
        logger.debug("init completed: %s", self.__class__)


    def singleSimulation(self):
        self.resetEnvironment()
        self.numberOfSimulationRuns = 100
        info_text = f"Simulating {self.numberOfSimulationRuns} runs interacting in {self.marketTiming} time in a {self.competition} competition with {self.marketSize} firms (alpha = {self.alpha}  delta = {self.delta} )"
        logger.info(info_text)
        self.simulate()

        logger.info("Simulation completed, exporting...")
        self.export()

    def heatmap(self):
        raise NotImplementedError("Didnt do this")

    def analyzeGamma(self):
        # desired scope of the weight to be analyzed
        weightStart = 0.0
        weightEnd = 1
        weightSteps = 0.01

        # fixed alpha and delta values as a framework to analyze gamma
        alphastart = 0.05
        alphaend = 0.15
        alphastep = 0.05

        deltastart = 0.8
        deltaend = 0.95
        deltastep = 0.05

        # total number of steps per parameter
        numberOfWeightSteps: int = int((weightEnd - weightStart + weightSteps) / weightSteps)
        numberOfAlpha: int = int((alphaend - alphastart + alphastep) / alphastep)
        numberOfDelta: int = int((deltaend - deltastart + deltastep) / deltastep)

        stepcounter: int = 1
        # indices for column and row
        c = 0
        r = 0

        # arrays to store results
        degree: List[List[float]] = [[0]*(numberOfAlpha * numberOfDelta)] * numberOfWeightSteps
        percentage = [[None]*(numberOfAlpha * numberOfDelta)] * numberOfWeightSteps

        print("Analyzing gamma at " + str(self.marketTiming) + " interaction in a " + str(self.competition) + " competition with " + str(self.marketSize) + " firms")

        i = alphastart
        while round(i, 3) <= alphaend:
            j = deltastart
            while round(j, 2) <= deltaend:
                k = weightStart
                while round(k, 3) <= weightEnd:

                    self.resetEnvironment()
                    self.alpha = round(i, 4)
                    self.delta = round(j, 4)
                    self.gamma = round(k, 4)
                    print(stepcounter, "/", (numberOfWeightSteps * numberOfAlpha * numberOfDelta), f"with (alpha = {self.alpha}  delta = {self.delta} at gamma = {self.gamma} ")

                    self.simulate()

                    degree[c][r] = get_mean(self.degrees)
                    percentage[c][r] = len(list(filter(lambda x: x < self.marketSize, self.pricesSD))) * 100.0 / self.numberOfSimulationRuns

                    c += 1
                    stepcounter += 1

                    k += weightSteps
                c = 0
                r += 1
                i += deltastep
            i += alphastep

        content = ""

        content += "alpha"
        for j in range(numberOfAlpha):
            for k in range(numberOfDelta):
                val = alphastart + j * alphastep
                content += f",{val:.4f}"

        content += "\ndelta"
        for j in range(numberOfAlpha):
            for k in range(numberOfDelta):
                val = alphastart + k * alphastep
                content += f",{val:.4f}"

        content += "\n \ngamma"
        for i in range(numberOfWeightSteps):
            content += "\n"
            val = weightStart + i * weightSteps
            content += f",{val:.4f}"

            for j in range(numberOfAlpha * numberOfDelta):
                val = degree[i][j]
                content += f",{val:.4f}"

        content += "\n \n"

        for i in range(numberOfWeightSteps):
            content += "\n"
            val = weightStart + i * weightSteps
            content += f",{val:.4f}"

            for j in range(numberOfAlpha * numberOfDelta):
                val = percentage[i][j]
                content += f",{val:.4f}"
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fn = f"{ts}_weightAnalysis_{self.alpha * 100}_{self.delta * 100}.csv"
        with open(fn, "w", encoding="utf8") as outfile:
            outfile.write(content)

    def resetEnvironment(self):
        self.prices = []
        self.pricesSD = []
        self.quantities = []
        self.profits = []
        self.degrees = []
        self.periods = []

        if self.marketTiming == "random" and self.competition == "cournot":
            if self.marketSize == 2:
                self.alpha = 0.100
                self.delta = 0.99
            elif self.marketSize == 3:
                self.alpha = 0.080
                self.delta = 0.87
                self.gamma = 1
            else:
                raise NotImplementedError("Did not bother")
        elif self.marketTiming == "discrete" and self.competition == "cournot":
            if self.marketSize == 2:
                self.alpha = 0.100
                self.delta = 0.99
            elif self.marketSize == 3:
                self.alpha = 0.100
                self.delta = 0.82
                self.gamma = 1.00
            else:
                raise NotImplementedError("Did not bother")
        else:
            print(self.marketTiming, self.competition)
            raise NotImplementedError("Did not bother")

    def simulate(self):
        self.startingTime = datetime.now()

        for counter in range(self.numberOfSimulationRuns):
            logger.info(f" - Period {counter +1 } of {self.numberOfSimulationRuns}")
            simulationRun = SimulationRun(seed=counter, sim_manager=self)
            simulationRun.simulate()

            self.storeData(
                simulationRun.getMeanPrice(),
                simulationRun.getSDPrice(),
                simulationRun.getMeanQuantity(),
                simulationRun.getMeanProfit(),
                simulationRun.getDegreeOfTacitCollusion(),
                simulationRun.getNumberOfPeriods())
        foo = len(list(filter(lambda x: x < self.marketSize, self.pricesSD))) * 100.0 / self.numberOfSimulationRuns
        print(f"  ->  Degree of Tacit Collusion: {get_mean(self.degrees)}; colluding in {foo} ")

    def storeData(self, price: float, priceSD: float, quantity: float, profit: float, degree: float, numberOfPeriods: int):
        self.prices.append(price)
        self.pricesSD.append(priceSD)
        self.quantities.append(quantity)
        self.profits.append(profit)
        self.degrees.append(degree)
        self.periods.append(float(numberOfPeriods))

    def export(self):
        end_time = datetime.now()
        duration = end_time - self.startingTime
        content = ""

        content += "SETTING"
        content += "\ntiming,"
        content += self.marketTiming

        if self.marketTiming == "discrete":
            content += f",,update interval,{self.updateInterval}"

        content += "\nmarket setting,"
        content += self.competition
        content += "\nmarket size,"
        content += str(self.marketSize)

        # simulation data and conditions
        content += "\n \nSIMULATION"
        content += "\nstart,"
        content += self.startingTime.strftime("%H:%M:%S")
        content += "\nduration,"
        content += str(duration)
        content += "\nend,"
        content += end_time.strftime("%H:%M:%S")
        content += "\nmax number of periods,"
        content += str(self.maxNumberOfPeriods)
        content += "\nnumber of runs,"
        content += str(self.numberOfSimulationRuns)
        content += "\nnumber of collusive runs,"
        foo = len(list(filter(lambda x: x < self.marketSize, self.pricesSD)))
        bar = foo / self.numberOfSimulationRuns * 100.0
        content += str(foo)
        content += ","
        content += str(bar)
        content += "%"

        # parameters of the Q-Learning algorithms
        content += "\n \nQ-LEARNING"
        content += "\nactionset,[0; "
        content += str(self.sizeOfActionSet - 1)
        content += "]"
        content += "\nalpha,"
        content += str(self.alpha)
        content += "\nbeta,"
        content += str(self.beta)

        if (self.marketSize > 2):
            content += "\ngamma,"
            content += str(self.gamma)
        content += "\ndelta,"
        content += str(self.delta)
        content += "\nØ epsilon at the end,"
        val = (math.exp(-self.beta * get_mean(self.periods)))
        content += f"{val:.8f}"

        content += "\n \nMEAN"
        content += "\nALL RUNS,mean,σ"
        content += "\nprice,"
        content += str(get_mean(self.prices))
        content += ","
        content += str(get_sd(self.prices))
        content += "\nσ (of all period prices),"
        content += str(get_mean(self.pricesSD))
        content += "\nquantity,"
        content += str(get_mean(self.quantities))
        content += ","
        content += str(get_sd(self.quantities))
        content += "\nprofit,"
        content += str(get_mean(self.profits))
        content += ","
        content += str(get_sd(self.profits))
        content += "\nperiods (in mio),"
        content += str(round(get_mean(self.periods) / 1000000, 3))
        content += ","
        content += str(round(get_sd(self.periods) / 1000000, 3))
        content += "\ndegree,"
        content += str(get_mean(self.degrees))
        content += ","
        content += str(get_sd(self.degrees))
        content += "\n \nDATA"
        content += "\ni,"
        content += "price,"
        content += "σ (of all prices),"
        content += "quantity,"
        content += "profit,"
        content += "periods (in mio),"
        content += "degree"
        content += "\n"

        for i in range(self.numberOfSimulationRuns):
            content += str(i + 1)
            content += ","
            content += str(self.prices[i])
            content += ","
            content += str(self.pricesSD[i])
            content += ","
            content += str(self.quantities[i])
            content += ","
            content += str(self.profits[i])
            content += ","
            content += str(round(self.periods[i] / 1000000, 3))
            content += ","
            content += str(self.degrees[i])
            content += "\n"

        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{ts}.csv"
        
        with open(filename, "w", encoding="utf8") as outfile:
            outfile.write(content)

        print("File " + filename + ".csv exported")


if __name__ == '__main__':

    SimulationManager().singleSimulation()
