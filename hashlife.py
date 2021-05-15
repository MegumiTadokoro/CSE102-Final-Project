# -*- coding: utf-8 -*-
"""
Created on Tue May  4 15:51:32 2021

@author: Nguyen Doan Dai
"""

import weakref, math

HC = weakref.WeakValueDictionary()

def hc(s):
    return HC.setdefault(s, s)

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

"""
Question 1: 
"""
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
    def __init__(self):
        # for the purpose of memoization
        self._cache = None
        
        # for the purposse of hash-consing
        self._hash = None
    
    def __hash__(self):
        if self._hash is None:
            self._hash = (
                self.population,
                self.level     ,
                self.nw        ,
                self.ne        ,
                self.sw        ,
                self.se        ,
            )
            self._hash = hash(self._hash)
        return self._hash
        
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, AbstractNode):
            return False
        return \
            self.level      == other.level      and \
            self.population == other.population and \
            self.nw         is other.nw         and \
            self.ne         is other.ne         and \
            self.sw         is other.sw         and \
            self.se         is other.se
    
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
      
    """
    Question 2: 
    """
    @staticmethod
    def zero(k):
        if k > 0:
            return AbstractNode().node( \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1), \
                AbstractNode().zero(k-1))
        else: return AbstractNode().cell(False)
      
    """
    Question 3: 
    """
    def extend(self):
        if self.level == 0:
            return AbstractNode().node(AbstractNode().cell(False), self, AbstractNode().cell(False), AbstractNode().cell(False))
        else:
            k = self.level - 1
            nw = AbstractNode().node(AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      self.nw)
            
            ne = AbstractNode().node(AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      self.ne, \
                      AbstractNode().zero(k))
            
            sw = AbstractNode().node(AbstractNode().zero(k), \
                      self.sw, \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k))
            
            se = AbstractNode().node(self.se, \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k), \
                      AbstractNode().zero(k))
            return AbstractNode().node(nw, ne, sw, se) 
      
    """
    Question 4, 5, and 8: 
    """
    def forward(self):
        if self.level < 2: return None
        
        """
        Question 9: it's trivial to see an universe with no population will not
        evolve, hence one does not need to make any calculation, and can return
        immediately an empty universe of appropriate size.
        """
        
        if self.population == 0:
            return self.zero(self.level - 1)
        
        """
        Question 5:
        """
        if self._cache is not None: return self._cache
        elif self.level == 2:
            
            """
            Original implementation____________________________________________
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
            """
            """
            Question 5:
            """
            """
            self._cache = AbstractNode().node(AbstractNode().cell((newTab[1][1])), \
                                              AbstractNode().cell((newTab[1][2])), \
                                              AbstractNode().cell((newTab[2][1])), \
                                              AbstractNode().cell((newTab[2][2])))
            __________________________________________________________________
            """
            
            """
            Question 10:
            """
            # Creating word w
            w = 0
            w |= self.nw.nw.alive << 15
            w |= self.nw.ne.alive << 14
            w |= self.ne.nw.alive << 13
            w |= self.ne.ne.alive << 12
            
            w |= self.nw.sw.alive << 11
            w |= self.nw.se.alive << 10
            w |= self.ne.sw.alive << 9
            w |= self.ne.se.alive << 8
            
            w |= self.sw.nw.alive << 7
            w |= self.sw.ne.alive << 6
            w |= self.se.nw.alive << 5
            w |= self.se.ne.alive << 4
            
            w |= self.sw.sw.alive << 3
            w |= self.sw.se.alive << 2
            w |= self.se.sw.alive << 1
            w |= self.se.se.alive
            
            #Bit-masking
            mask = 0b11101010111
            cnt = 0
            
            #se
            wp = w & mask
            while wp: cnt += 1; wp &= (wp - 1)
            se = (((w>>5)&1) and cnt == 2) or cnt == 3
            
            #sw
            cnt = 0; wp = w & (mask << 1)
            while wp: cnt += 1; wp &= (wp - 1)
            sw = (((w>>6)&1) and cnt == 2) or cnt == 3
            
            #ne
            cnt = 0; wp = w & (mask << 4)
            while wp: cnt += 1; wp &= (wp - 1)
            ne = (((w>>9)&1) and cnt == 2) or cnt == 3
            
            #nw
            cnt = 0; wp = w & (mask << 5)
            while wp: cnt += 1; wp &= (wp - 1)
            nw = (((w>>10)&1) and cnt == 2) or cnt == 3
            
            self._cache = AbstractNode().node(AbstractNode().cell(nw), \
                                              AbstractNode().cell(ne), \
                                              AbstractNode().cell(sw), \
                                              AbstractNode().cell(se))
        else:
            # the variables' name follow notation used in statement
            
            # Step 1: calculate the first 2^(k-3) generations
            R_nw = self.nw.forward()
            R_tc = AbstractNode().node(self.nw.ne, self.ne.nw, self.nw.se, self.ne.sw).forward()
            R_ne = self.ne.forward()
            
            R_cl = AbstractNode().node(self.nw.sw, self.nw.se, self.sw.nw, self.sw.ne).forward()
            R_cc = AbstractNode().node(self.nw.se, self.ne.sw, self.sw.ne, self.se.nw).forward()
            R_cr = AbstractNode().node(self.ne.sw, self.ne.se, self.se.nw, self.se.ne).forward()
            
            R_sw = self.sw.forward()
            R_bc = AbstractNode().node(self.sw.ne, self.se.nw, self.sw.se, self.se.sw).forward()
            R_se = self.se.forward()
            
            # Step 2: calculate the second 2^(k-3) generations
            
            B_nw = AbstractNode().node(R_nw, R_tc, R_cl, R_cc).forward()
            B_ne = AbstractNode().node(R_tc, R_ne, R_cc, R_cr).forward()
            B_sw = AbstractNode().node(R_cl, R_cc, R_sw, R_bc).forward()
            B_se = AbstractNode().node(R_cc, R_cr, R_bc, R_se).forward()
            
            """
            Question 5:
            """
            self._cache = AbstractNode().node(B_nw, B_ne, B_sw, B_se)
            
        return self._cache
    
    """
    Question 6:
    """
    @staticmethod
    def canon(node):
        return HC.setdefault(node, default = node)
    
    """
    Question 7:
    """
    @staticmethod
    def cell(alive):
        return AbstractNode().canon(CellNode(alive))
    
    """
    Question 7:
    """
    @staticmethod
    def node(nw, ne, sw, se):
        return AbstractNode().canon(Node(nw, ne, sw, se))
            
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

#------------------------------------------------------------------------------
class HashLifeUniverse(Universe):
    def __init__(self, *args):
        if len(args) == 1:
            self._root = args[0]
        else:
            self._root = HashLifeUniverse.load(*args)

        self._generation = 0

    @staticmethod
    def load(n, m, cells):
        level = math.ceil(math.log(max(1, n, m), 2))

        mkcell = getattr(AbstractNode, 'cell', CellNode)
        mknode = getattr(AbstractNode, 'node', Node    )

        def get(i, j):
            i, j = i + n // 2, j + m // 2
            return \
                i in range(n) and \
                j in range(m) and \
                cells[i][j]
                
        def create(i, j, level):
            if level == 0:
                return mkcell(get (i, j))

            noffset = 1 if level < 2 else 1 << (level - 2)
            poffset = 0 if level < 2 else 1 << (level - 2)

            nw = create(i-noffset, j+poffset, level - 1)
            sw = create(i-noffset, j-noffset, level - 1)
            ne = create(i+poffset, j+poffset, level - 1)
            se = create(i+poffset, j-noffset, level - 1)

            return mknode(nw=nw, ne=ne, sw=sw, se=se)
                
        return create(0, 0, level)
    
    """
    Question 11:
    """
    def get(self, i, j):
        try:
            level = self._root.level
            if i == 0 and j == 0: return self._root.alive
            x = (i<<1) + (1 << (level - 1))
            y = (j<<1) + (1 << (level - 1))
            if i < 0 and j < 0: return self._root.nw.get(x, y)
            if i < 0 and j > 0: return self._root.sw.get(x, y)
            if i > 0 and j < 0: return self._root.ne.get(x, y)
            if i > 0 and j > 0: return self._root.se.get(x, y)
            return None
        except AttributeError:
            return False
    
    """
    Question 12:
    """
    def extend(self, k):
        treeExtended =  self._root.extend()
        while treeExtended.level < max(k, 2): treeExtended = treeExtended.extend()
        return treeExtended

    def rounds(self, n):
        # Do something here
        raise NotImplementedError()

    def round(self):
        return self.rounds(1)

    @property
    def root(self):
        return self._root
        
    @property
    def generation(self):
        return self._generation