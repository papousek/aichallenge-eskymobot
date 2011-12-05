import heapq
from collections import deque
from ants import LAND
from Maps import UNCHARTED
from math import sqrt

#TODO There is no need to calculated the whole potential field during update, find a better way

class PotentialField:
    """ PotentialField represents a map with information about somehow defined
    intensity in it"""
    
    def __init__(self):
        self.rows = None
        self.cols = None
        self.field = None
        self.driver = None
        self.terrain = None
        
    def setup(self, driver, terrain):
        """ Initializes this potential field (allocates its variables) """
        self.rows = driver.rows
        self.cols = driver.cols
        self.field = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.driver = driver
        self.terrain = terrain

    def get_at(self, (row, col)):
        """ Returns raw data in potential field """
        return self.field[row][col]

    def set_at(self, (row, col), value):
        """ Sets raw data in potential field """
        self.field[row][col] = value

    def get_potential(self, loc, none_value, poten_func):
        """ Computes potential on specified position in the field """
        if self.get_at(loc) == None:
            return none_value
        else:
            return poten_func(self.get_at(loc))

class PotentialFieldWithSources(PotentialField):
    def __init__(self):
        PotentialField.__init__(self)
        self.sources = None
        
    def setup(self, driver, terrain):
        PotentialField.setup(self, driver, terrain)
        self.sources = [[set() for col in range(self.driver.cols)] for row in range(self.driver.rows)]

    def merge_sources(self, loc, sources):
        row, col = loc
        self.sources[row][col].update(sources)
        
    def get_at_sources(self, loc):
        row, col = loc
        return self.sources[row][col]
        
    def spread(self, sources, depth_limit):
        """ Spreads the intensity from specified sources using distances of the sources. Assumes self.sources is full of empty sets """
        q = deque()
        for source in sources:
            self.init_potential(source, depth_limit)
            row, col = source
            if self.is_source_expansion_allowed():
                self.sources[row][col].add(source)
            q.append(source)

        # Expand sources
        while len(q) > 0:
            loc = q.popleft()
            for to_spread in [pos for pos in self.driver.neighbours(loc)
                             if self.terrain.get_at(pos) == LAND]:
                (insert_to_queue, spread_sources) =  self.spread_potential(loc, to_spread, depth_limit)
                if (insert_to_queue):
                    q.append(to_spread)
                if spread_sources and self.is_source_expansion_allowed():
                    self.merge_sources(to_spread, self.get_at_sources(loc))
    
    def get_sources(self):
        return []
    
    def update(self, depth):
        self.sources = [[set() for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.field = [[None for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.spread(self.get_sources(), depth)

    def render_text_map(self, render_sources = None):
        if render_sources == None:
            render_sources = False
        tmp = ''
        for row in range(self.driver.rows):
            tmp += '# '
            for col in range(self.driver.cols):
                val = self.get_at((row, col))
                if val == None:
                    tmp += '   ?   '
                else:
                    tmp += ' (%3i' % val
                    if render_sources: 
                        tmp += str(self.get_at_sources((row, col)))
                    tmp += ') '
            tmp += '\n'
        tmp += '\n'
        return tmp
 
    def is_source_expansion_allowed(self):
        return True 

    def init_potential(self, loc, depth_limit):
        self.set_at(loc, 0)

    """ Vraci (bool, bool) -- (toto policko ma dale sirit potencial, ma se rozsirit zdroj) """
    def spread_potential(self, loc_from, loc_to, depth_limit):
        if self.get_at(loc_to) == None:
            self.set_at(loc_to, self.get_at(loc_from) + 1)
            if self.get_at(loc_to)  < depth_limit:
                return (True, True)
            else:
                return (False, True)
        elif self.get_at(loc_to) == self.get_at(loc_from) + 1:
            return (False, True)
        else:
            return (False, False)
            

class FoodPotentialFieldWithSources(PotentialFieldWithSources):
        
    def get_sources(self):
        return self.driver.all_food()

class EnemyHillPotentialField(PotentialFieldWithSources):

    def get_sources(self):
        return self.driver.all_enemy_hills()

    def is_source_expansion_allowed(self):
        return False

class UnchartedPotentialField(PotentialFieldWithSources):

    def get_sources(self):
        uncharted = [(row, col) for row in range(self.driver.rows) for col in range(self.driver.cols)
                if self.terrain.get_at((row,col)) == UNCHARTED]
        return uncharted

    def is_source_expansion_allowed(self):
        return False

class NotVisibleChartedPotentialField(PotentialFieldWithSources):

    def get_sources(self):
        not_visible_charted = [(row, col) for row in range(self.driver.rows) for col in range(self.driver.cols)
                if self.terrain.get_at((row,col)) == LAND and not self.driver.visible((row, col))]        
        return not_visible_charted
   
    def is_source_expansion_allowed(self):
        return False 

class AntsPotentialField(PotentialField):
    
    def get_at(self, loc):
        if (PotentialField.get_at(self, loc) == None):
            self.compute_at(loc)
        return PotentialField.get_at(self, loc)

    def update(self):
        self.field = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.enemy_ants = {}
        for ant_loc, player in self.driver.enemy_ants():
            if not player in self.enemy_ants:
                self.enemy_ants[player] = []
            self.enemy_ants[player].append(ant_loc)

    def compute_at(self, loc):
        enemy_radius2 = int(sqrt(self.driver.attackradius2) + 1) ** 2 
        my_radius2 = self.driver.attackradius2
        enemy_potential = 0
        for ant, player in self.driver.enemy_ants():
            if self.driver.radius2(loc, ant) <= enemy_radius2:
                enemy_ant_potential = 0
                for neigh_ant in self.enemy_ants[player]:
                    if self.driver.radius2(ant, neigh_ant) <= enemy_radius2:
                        enemy_ant_potential = enemy_ant_potential + 1
                enemy_potential = max(enemy_ant_potential, enemy_potential)
        my_potential = 0
        for ant in self.driver.my_ants():
            if self.driver.radius2(loc, ant) <= my_radius2:
                    my_potential = my_potential + 1 
        self.set_at(loc, my_potential - enemy_potential)

    def render_text_map(self):
        tmp = ''
        for row in range(self.driver.rows):
            tmp += '# '
            for col in range(self.driver.cols):
                val = self.field[row][col]
                if val == None:
                    tmp += '  ?  '
                else:
                    tmp += '%3i' % val
                    tmp += '  '
            tmp += '\n'
        tmp += '\n'
        return tmp
