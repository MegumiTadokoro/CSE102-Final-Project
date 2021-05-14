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
    
    @property
    def m(self):
        return self.__m
    
    def get(self, i, j):
        return self.__cells[i][j]
    
    def toggle(self, i, j):
        self.__cells[i][j] ^= True
    
    """Compute the number of alive neighbors"""
    def __getAliveNeighbors(self, x, y):
        cnt = 0
        for dx in range(x-1, x+2):
            for dy in range(y-1, y+2): 
                if dx == x and dy == y: continue
                if dx >= 0 and dx < self.n and dy >= 0 and dy < self.m and self.get(dx, dy): cnt += 1
        return cnt
    
    """Compute the next generation of naive universe"""
    def round(self):
        toggle = set()
        for i in range(self.n):
            for j in range(self.m):
                aliveNeighbors = self.__getAliveNeighbors(i, j)
                if self.get(i, j) and (aliveNeighbors < 2 or aliveNeighbors > 3): toggle.add((i, j))
                if not self.get(i, j) and aliveNeighbors == 3: toggle.add((i, j))
        for (i, j) in toggle: self.toggle(i, j)

class AbstractNode:
    @property
    def level(self):
        """Level of this node"""
        return self.ne.level + 1 if self.ne is not None else 1

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
        if k > 0:
            return Node( \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1))
        else: return CellNode(False)
    
    def extend(self):
        if self.level == 0:
            return Node(CellNode(False), self, CellNode(False), CellNode(False))
        else:
            k = self.level - 1
            nw = Node(AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      self.nw)
            
            ne = Node(AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      self.ne, \
                      AbstractNode().zero(k))
            
            sw = Node(AbstractNode().zero(k), \
                      self.sw, \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k))
            
            se = Node(self.se, \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k))
            return Node(nw, ne, sw, se) 
    
    def forward(self):
        if self.level < 2: return None
        elif self.level == 2:
            # temporary variable
            temp = [[False for _ in range(4)] for _ in range(4)]
            newTab = [[False for _ in range(4)] for _ in range(4)]
            
            # translate to table representation
            temp[0][0] = self.nw.nw.alive
            temp[0][1] = self.nw.ne.alive
            temp[0][2] = self.ne.nw.alive
            temp[0][3] = self.ne.ne.alive
            
            temp[1][0] = self.nw.sw.alive
            temp[1][1] = self.nw.se.alive
            temp[1][2] = self.ne.sw.alive
            temp[1][3] = self.ne.se.alive
            
            temp[2][0] = self.sw.nw.alive
            temp[2][1] = self.sw.ne.alive
            temp[2][2] = self.se.nw.alive
            temp[2][3] = self.se.ne.alive
            
            temp[3][0] = self.sw.sw.alive
            temp[3][1] = self.sw.se.alive
            temp[3][2] = self.se.sw.alive
            temp[3][3] = self.se.se.alive
            
            # compute the next generation
            for x in range(4):
                for y in range(4):
                    cnt = 0
                    
                    # compute the number of alive neighbors
                    for dx in range(x-1, x+2):
                        for dy in range(y-1, y+2):
                            if dx == x and dy == y: continue
                            if dx >= 0 and dx < 4 and dy >= 0 and dy < 4 and temp[dx][dy]: cnt += 1
                    
                    # Conway's rule
                    if not temp[x][y]: newTab[x][y] = (cnt == 3)
                    else: newTab[x][y] = (cnt == 2 or cnt == 3)
            
            # translate to QuadTree representation
            return Node(CellNode((newTab[1][1])), \
                        CellNode((newTab[1][2])), \
                        CellNode((newTab[2][1])), \
                        CellNode((newTab[2][2])))
        else:
            # the variables' name follow notation used in statement
            
            # Step 1: calculate the first 2^(k-3) generations
            R_nw = self.nw.forward()
            R_tc = Node(self.nw.ne, self.ne.nw, self.nw.se, self.ne.sw).forward()
            R_ne = self.ne.forward()
            
            R_cl = Node(self.nw.sw, self.nw.se, self.sw.nw, self.sw.ne).forward()
            R_cc = Node(self.nw.se, self.ne.sw, self.sw.ne, self.se.nw).forward()
            R_cr = Node(self.ne.sw, self.ne.se, self.se.nw, self.se.ne).forward()
            
            R_sw = self.sw.forward()
            R_bc = Node(self.sw.ne, self.se.nw, self.sw.se, self.se.sw).forward()
            R_se = self.se.forward()
            
            # Step 2: calculate the second 2^(k-3) generations
            
            B_nw = Node(R_nw, R_tc, R_cl, R_cc).forward()
            B_ne = Node(R_tc, R_ne, R_cc, R_cr).forward()
            B_sw = Node(R_cl, R_cc, R_sw, R_bc).forward()
            B_se = Node(R_cc, R_cr, R_bc, R_se).forward()
            
            return Node(B_nw, B_ne, B_sw, B_se)
                        
            
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