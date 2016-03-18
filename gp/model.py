from gp.gene import Gene

class GPModel:
    def __init__(self, args=None, populationSize=None, maxGeneration=None,
            mutateRate=None, eliteRate=None, crossRate=None,
            crossType=None, verifyNum=None, proof=None, tactics=None):
        self.populationSize = populationSize or args.populationSize
        self.maxGeneration = maxGeneration or args.maxGeneration
        self.mutateRate = mutateRate or args.mutateRate
        self.eliteRate = eliteRate or args.eliteRate
        self.crossRate = crossRate or args.crossRate
        self.crossType = crossType or args.crossType
        self.verifyNum = verifyNum or args.verifyNum
        self.proof = proof
        self.tactics = tactics

    def showProp(self):
        print(self.populationSize)
        print(self.maxGeneration)
        print(self.mutateRate)
        print(self.eliteRate)
        print(self.crossRate)
        print(self.crossType)
        print(self.verifyNum)
        print(self.proof)

    def initPopulation(self, size):
        self.population = []
        for individual in range(size):
            self.population.append(Gene(self.tactics))

    def initProcess(self):
        self.currentGeneration = 1
        self.provedIndividual = None

    def nextGeneration(self):
        self.currentGeneration += 1

    def calculateFitness(self):
        # return individual if theorem is proved, o.w return None
        for (index, gene) in enumerate(self.population):
            (isProved, fitness) = self.proof.calculateFitness(gene.chromosome)
            print("{0} {1}".format(index, fitness))
            gene.updateFitness(fitness)
            self.population[index] = gene
            if isProved:
                return index
        return None

    def crossover(self):
        pass

    def mutate(self):
        pass

    def start(self):
        self.initPopulation(self.populationSize)
        self.initProcess()
        while (True):
            # if (self.currentGeneration > self.maxGeneration):
            if (self.currentGeneration > 1):
                break;
            print("Generation No.{0}".format(self.currentGeneration))
            self.provedIndividual = self.calculateFitness()
            if self.provedIndividual is not None:
                break;
            self.crossover()
            self.mutate()
            self.nextGeneration()

    def isProved(self):
        if self.provedIndividual is None:
            return False
        else:
            return True
