# -*- coding: utf-8 -*-
"""
Created on Tue May  4 15:51:32 2021

@author: ngdda
"""

class Universe:
    def round(self):
        """Compute (in place) the next generation of the universe"""
        raise NotImplementedError

    def get(self, i, j):
        """Returns the state of the cell at coordinates (ij[0], ij[1])"""
        raise NotImplementedError

    def rounds(self, n):
        """Compute (in place) the n-th next generation of the universe"""
        for _i in range(n):
            self.round()

class NaiveUniverse(Universe):
    def __init__(self, n, m, cells):
        self.__n = n
        self.__m = m
        self.__cells = cells
    
    @property
    def n(self):
        return self.__n
    
    def m(self):
        return self.__m
    
    @property
    def get(self, i, j):
        return self.__cells[i][j]
    
    @get.setter
    def toggle(self, i, j):
        self.__cell[i][j] ^= 1
    
    """Compute the number of alive neighbors"""
    def getAliveNeighbors(self, x, y):
        cnt = 0
        for dx in range(x-1, x+2):
            for dy in range(y-1, y+2): 
                if dx == x and dy == y: continue
                if dx >= 0 and dx < self.n and dy >= 0 and dy < self.m and self.get(dx, dy): cnt += 1
        return cnt
    
    """Compute the next generation of naive universe"""
    def round(self):
        for i in range(self.n):
            for j in range(self.m):
                aliveNeighbors = self.getAliveNeighbors(i, j)
                if self.get(i, j) and (aliveNeighbors < 2 or aliveNeighbors > 3): self.toggle(i, j)
                if not self.get(i, j) and aliveNeighbors == 3: self.toggle(i, j)

class AbstractNode:
    @property
    def level(self):
        """Level of this node"""
        raise NotImplementedError()

    @property
    def population(self):
        """Total population of the area"""
        raise NotImplementedError()

    nw = property(lambda self : None)
    ne = property(lambda self : None)
    sw = property(lambda self : None)
    se = property(lambda self : None)
    
    @staticmethod
    def zero(k):
        node = AbstractNode()
        if k > 0: 
            node.nw = node.zero(k-1)
            node.ne = node.zero(k-1)
            node.sw = node.zero(k-1)
            node.se = node.zero(k-1)
        return node
    
    def extend(self):
        node = AbstractNode()
        node.nw = node.zero(self.level)
        node.ne = node.zero(self.level)
        node.sw = node.zero(self.level)
        node.se = node.zero(self.level)
        
        if self.level == 0:
            node.ne = self
        else:
            node.nw.se = self.nw
            node.ne.sw = self.ne
            node.sw.ne = self.sw
            node.se.nw = self.se
            
        return node
    
    def forward(self):
        if self.level < 2: return None
        elif self.level == 2:
            # temporary variable
            temp = [[0 for _ in range(4)] for _ in range(4)]
            newTab = [[0 for _ in range(4)] for _ in range(4)]
            
            # translate to table representation
            for i in range(4):
                if i == 0: node = self.nw
                if i == 1: node = self.ne
                if i == 2: node = self.sw
                if i == 3: node = self.se
                temp[i][0] = node.nw
                temp[i][1] = node.ne
                temp[i][2] = node.sw
                temp[i][3] = node.se
            
            # compute the next generation
            for x in range(4):
                for y in range(4):
                    cnt = 0
                    
                    # compute the number of alive neighbors
                    for dx in range(x-1, x+2):
                        for dy in range(y-1, y+2):
                            if dx == x and dy == y: continue
                            if dx >= 0 and dx < 4 and dy >= 0 and dy < 4 and temp[x][y]: cnt += 1
                    
                    # Conway's rule
                    if not temp[x][y]: newTab[x][y] = (cnt == 3)
                    else: newTab[x][y] = (cnt == 2 or cnt == 3)
            
            # translate to QuadTree representation
            for i in range(4):
                if i == 0: node = self.nw
                if i == 1: node = self.ne
                if i == 2: node = self.sw
                if i == 3: node = self.se
                node.nw = newTab[i][0]
                node.ne = newTab[i][1]
                node.sw = newTab[i][2]
                node.se = newTab[i][3]
        else:
            pass
                        
            
class CellNode(AbstractNode):
    def __init__(self, alive):
        super().__init__()

        self._alive = bool(alive)

    level      = property(lambda self : 0)
    population = property(lambda self : int(self._alive))
    alive      = property(lambda self : self._alive)

class Node(AbstractNode):
    def __init__(self, nw, ne, sw, se):
        super().__init__()

        self._level      = 1 + nw.level
        self._population =  \
            nw.population + \
            ne.population + \
            sw.population + \
            se.population
        self._nw = nw
        self._ne = ne
        self._sw = sw
        self._se = se

    level      = property(lambda self : self._level)
    population = property(lambda self : self._population)

    nw = property(lambda self : self._nw)
    ne = property(lambda self : self._ne)
    sw = property(lambda self : self._sw)
    se = property(lambda self : self._se)