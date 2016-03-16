class Proof:
    def __init__(self, inputFile):
        self.theorem = self.readThmFromFile(inputFile)

    def readThmFromFile(self, inputFile):
        retList = []
        for line in inputFile:
            retList.append(line.strip())
        return retList
