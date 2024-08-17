from abc import ABC, abstractmethod

import copy
class State(ABC):
    @abstractmethod
    def isEnd(self):
        pass

    @abstractmethod
    #Get value of this state. Win for first player is infinity, win for second player is -infinity, draw is 0
    def value(self):
        pass

    @abstractmethod
    def isFirstPlayerTurn(self):
        pass

    @abstractmethod
    def getAllPossibleMoves(self):
        pass

    @abstractmethod
    def hash(self):
        pass

    def __hash__(self):
        return hash(self.hash())

    def copy(self):
        return copy.deepcopy(self)


