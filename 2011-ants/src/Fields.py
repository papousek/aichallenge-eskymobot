import heapq
from collections import deque
from ants import LAND
from Maps import *
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
        if self.is_source_expansion_allowed():
            self.sources = [[set() for col in range(self.driver.cols)] for row in range(self.driver.rows)]   
        self.to_spread_list = []

    def merge_sources(self, loc, sources):
        row, col = loc
        self.sources[row][col].update(sources)
        
    def get_at_sources(self, loc):
        row, col = loc
        return self.sources[row][col]
        
    def initialize_source(self, (row,col), depth_limit):
        self.init_potential((row,col), depth_limit)
        if self.is_source_expansion_allowed():
            self.sources[row][col].add((row,col))
    
    def expand_source(self, source, depth_limit, step_limit):
        next_sources = []
        for to_spread in [pos for pos in self.driver.neighbours(source) if self.terrain.get_at(pos) == LAND]:
            (insert_to_queue, spread_sources) = self.spread_potential(source, to_spread, depth_limit)
            if insert_to_queue:
                next_sources.append(to_spread)
            if spread_sources and self.is_source_expansion_allowed():
                self.merge_sources(to_spread, self.get_at_sources(source))
        return next_sources
    
    def spread(self, sources, depth_limit, step_limit):
        """ Spreads the intensity from specified sources using distances of the sources. Assumes self.sources is full of empty sets """
        map(lambda source: self.initialize_source(source, depth_limit), filter(lambda source: self.get_at(source) == None, sources))
        self.to_spread_list.extend(sources)

        # Expand sources
        num_of_steps = 0
        while len(self.to_spread_list) > 0:
            self.to_spread_list = reduce(lambda x,y:x+y, map(lambda source: self.expand_source(source, depth_limit, step_limit), self.to_spread_list), [])
            self.to_spread_list = list(set(self.to_spread_list))
            num_of_steps += len(self.to_spread_list)
            if step_limit != None and num_of_steps >= step_limit:
                return

    def get_sources(self):
        return []
    
    def update(self, depth_limit = None, step_limit = None):
        if self.is_source_expansion_allowed():
            self.sources = [[set() for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.field = [[None for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.to_spread_list = []
        self.spread(self.get_sources(), depth_limit, step_limit)

    def render_text_map(self, render_sources = None):
        if render_sources == None:
            render_sources = False
        tmp = ''
        for row in range(self.driver.rows):
            tmp += '# '
            for col in range(self.driver.cols):
                val = self.get_at((row, col))
                if val == None:
                    if self.terrain.get_at((row, col)) == LAND:
                        tmp += '  ?  '
                    elif self.terrain.get_at((row, col)) == UNCHARTED:
                        tmp += '  U  '
                    elif self.terrain.get_at((row, col)) == WATER:
                        tmp += '  #  '
                else:
                    tmp += '%3i' % val
                    if render_sources:
                        tmp += str(self.get_at_sources((row, col)))
                    tmp += '  '
            tmp += '\n'
        tmp += '\n'
        return tmp
 
    def is_source_expansion_allowed(self):
        """ Expanduje pouze vzdalenosti, nikoliv zdroje """ 
        return True

    def init_potential(self, loc, depth_limit):
        self.set_at(loc, 0)

    def is_valid(self, loc):
        return self.get_at(loc) == 0 or reduce(lambda x, y: x or y, [self.get_at(neigh) < self.get_at(loc) for neigh in self.driver.neighbours(loc) if self.get_at(neigh) != None], False)
        
    """ Vraci (bool, bool) -- (toto policko ma dale sirit potencial, ma se rozsirit zdroj) """
    def spread_potential(self, loc_from, loc_to, depth_limit):
        if self.get_at(loc_to) == None or self.get_at(loc_to) > (self.get_at(loc_from) + 1):
            self.set_at(loc_to, self.get_at(loc_from) + 1)
            if depth_limit == None or self.get_at(loc_to) < depth_limit:
                return (True, True)
            else:
                return (False, True)
        elif self.get_at(loc_to) == self.get_at(loc_from) + 1:
            return (False, True)
        else:
            return (False, False)
 
class FogPotentialField(PotentialFieldWithSources):

    def get_sources(self):
        not_visible_charted = [(row, col) for row in range(self.driver.rows) for col in range(self.driver.cols)
                if self.terrain.get_at((row,col)) == LAND and not self.driver.visible((row, col))]
        return not_visible_charted

    def is_source_expansion_allowed(self):
        return False 
 
class FoodPotentialFieldWithSources(PotentialFieldWithSources):
        
    def get_sources(self):
        return self.driver.all_food()

class MostlyStaticPotentialField(PotentialFieldWithSources):

    def __init__(self):
        PotentialFieldWithSources.__init__(self)

    def update(self, depth_limit = None, step_limit = None):
        tmp = [self.driver.neighbours(loc) for loc in self.terrain.new_fields]
        new_fields = filter(lambda loc: self.terrain.get_at(loc) == LAND and self.get_at(loc) != None, [neigh for neighs in tmp for neigh in neighs])
        self.to_spread_list.extend(set(new_fields))
        self.spread(self.get_sources(), depth_limit, step_limit)

    """ Vraci (bool, bool) -- (toto policko ma dale sirit potencial, ma se rozsirit zdroj) """
    def spread_potential(self, loc_from, loc_to, depth_limit):
        if self.get_at(loc_to) == None or self.get_at(loc_to) > (self.get_at(loc_from) + 1) or not self.is_valid(loc_to):
            self.set_at(loc_to, self.get_at(loc_from) + 1)
            if depth_limit == None or self.get_at(loc_to) < depth_limit:
                return (True, True)
            else:
                return (False, True)
        elif self.get_at(loc_to) == self.get_at(loc_from) + 1:
            return (False, True)
        else:
            return (False, False)
        
class UnchartedPotentialField(MostlyStaticPotentialField):

    def is_source_expansion_allowed(self):
        return False

    def update(self, depth_limit = None, step_limit = None):
        self.uncharted_sources = None
        PotentialFieldWithSources.update(self, depth_limit, step_limit)
        #MostlyStaticPotentialField.update(self, depth_limit, step_limit)
        
    def get_sources(self):
        if self.uncharted_sources == None:
            is_uncharted = lambda loc: self.terrain.get_at(loc) == UNCHARTED
            is_uncharted_source = lambda loc: is_uncharted(loc) and [neigh for neigh in self.driver.neighbours(loc) if not is_uncharted(neigh)]
            self.uncharted_sources = [(row, col) for row in range(self.driver.rows) for col in range(self.driver.cols)
                    if is_uncharted_source((row, col))]
        return self.uncharted_sources

class EnemyHillPotentialField(MostlyStaticPotentialField):

    def __init__(self):
        MostlyStaticPotentialField.__init__(self)
        self.prev_sources = []
        self.new_sources = []
        
    def is_source_expansion_allowed(self):
        return False

    def get_sources(self):
        return self.new_sources

    def update(self, depth_limit = None, step_limit = None):
        all_sources = self.driver.driver_enemy_hills[:]
        if len(set(self.prev_sources) - set(all_sources)) > 0:
            #Some sources were removed
            self.new_sources = all_sources[:]
            PotentialFieldWithSources.update(self, depth_limit, step_limit)
            self.prev_sources = all_sources[:]
        else:
            self.new_sources = list(set(all_sources) - set(self.prev_sources))
            MostlyStaticPotentialField.update(self, depth_limit, step_limit)
            self.prev_sources = all_sources[:]
            
        