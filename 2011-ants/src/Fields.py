import heapq
from collections import deque
from ants import LAND
from Maps import UNCHARTED

#TODO There is no need to calculated the whole potential field during update, find a better way

class PriorityQueue:
    def __init__(self):
        self.queue = []
    
    def empty(self):
        return self.queue == []
    
    def put(self, (priority, value)):
        heapq.heappush(self.queue, (priority, value))
    
    def get(self):
        priority, value = heapq.heappop(self.queue)
        return (priority, value)

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
        
class MinLandIntegerPotentialField(PotentialField):
    """ MinChartedIntegerPotentialField represents a PotentialField with intensity based
    on integer distances of sources. Sources represents objects with the highest intensity
    (e.g. food). Intensity spreads to four neighbour fields by incrementing their distance
    from a source. On places where intensity from two or more sources are present
    the lower distance is taken. Intensity does not spread to uncharted fields and it
    spreads only to LANDs.
    """
    
    def __init__(self):
        PotentialField.__init__(self)
        self.driver = None
        self.terrain = None
        self.sources = None
    
    def setup(self, driver, terrain):
        """ Initializes this potential field (allocates its variables) """
        self.rows = driver.rows
        self.cols = driver.cols
        self.field = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.driver = driver
        self.terrain = terrain
        self.sources = []

    def get_potential(self, loc, none_value, poten_func):
        """ Computes potential on specified position in the field """
        if self.get_at(loc) == None:
            return none_value
        else:
            return poten_func(self.get_at(loc))
        
    def remove_fields_of_source(self, source):
        """ Finds fields whose intensity is influenced by specified source and removes
        intensity from them (set the distance to None). Returns list of those fiels (in any order).
        """
        if (self.get_at(source) == None):
            return []
            
        self.set_at(source, None)
        removed = [source]
        fields_to_check = deque([loc for loc in self.driver.neighbours(source) if self.get_at(loc) != None and self.get_at(loc) > distance])
        while not fields_to_check.empty():
            loc = fields_to_check.pop()

            # Find whether there is a field with lower distance than distance of this field
            # If such field exists do nothing, otherwise remove the field and try its neighbours
            neighs = self.driver.neighbours(loc)
            if not reduce(lambda prev, loc: prev or (self.get_at(loc) != None and self.get_at(loc) < distance), neighs, False):
                removed.append(loc)
                self.set_at(loc, None)
                fields_to_check.extendleft([loc for loc in neighs if self.get_at(loc) != None and self.get_at(loc) > distance])
                
        return removed        
    
    def spread(self, sources):
        """ Spreads the intensity from specified sources using distances of the sources """
        q = PriorityQueue()
        for source in self.sources:
            if self.get_at(source) != None:
                q.put((self.get_at(source), source))

        # Expand sources
        while not q.empty():
            distance, loc = q.get()
            for next_source in [pos for pos in self.driver.neighbours(loc)
                            if self.terrain.get_at(pos) == LAND and (self.get_at(pos) == None or self.get_at(pos) > (distance+1))]:
                self.set_at(next_source,distance + 1)
                q.put((distance + 1, next_source))
        
    def update_fields(self, fields):
        """ Updates distances of specified fields """
        for loc in fields:
            self.set_at(loc, None)
        valid_neighbours_list = [[valids for valids in self.driver.neighbours(loc) if self.get_at(valids) != None] for loc in fields]
        # collapse valid_neighbours_list to one list
        valid_neightbours = reduce(lambda l,r: l + r, valid_neighbours_list)
        self.spread(valid_neighbours)
        
    def add_source(self, source):
        """ Adds new source and updates the field """
        self.set_at(source, 0)
        self.sources.append(source)
        self.spread([source])
        
    def add_sources(self, sources):
        """ Adds new list of sources and updates the field """
        for source in sources:
            self.set_at(source, 0)
        self.sources.extend(sources)
        self.spread(sources)

    def remove_source(self, source):
        """ Removes a source and updates the field """
        to_update = self.remove_fields_of_source(source)
        try:
            self.sources.remove(source)
        except:
            pass
        self.update_fields(to_update)
        
    def remove_sources(self, sources):
        """ Removes list of sources and updates the field """
        to_update = reduce(lambda l,r: l+r, [self.remove_fields_of_source(source) for source in sources])
        for source in sources:
            try:
                self.sources.remove(source)
            except:
                pass
        self.update_fields(to_update)

    def recalculate(self):
        """ Recalculates the whole field """
        self.field = [[None for col in range(self.cols)] for row in range(self.rows)]
        for source in self.sources:
            self.set_at(source, 0)
        self.spread(self.sources)
    
    def render_text_map(self):
        tmp = ''
        for row in self.field:
            tmp += '# '
            for val in row:
                if val == None:
                    tmp += '%3i' % (-1)
                else:
                    tmp += '%3i' % val
            tmp += '\n'
        tmp += '\n'
        return tmp

class FoodPotentialField(MinLandIntegerPotentialField):
    """ FoodPotentialField represents potential field where places with food has intensity value 0"""

    def __init__(self):
        MinLandIntegerPotentialField.__init__(self)
        
    def setup(self, driver, terrain):
        """ Initializes the field """
        MinLandIntegerPotentialField.setup(self, driver, terrain)
        
    def update(self):
        """ Updates this object """
        # just a simple implementation
        self.sources = self.driver.food_list[:]
        self.recalculate()
            
class EnemyHillPotentialField(MinLandIntegerPotentialField):
    """ EnemyHillPotentialField represents potential field where places with enemy fills has intensity value 0"""

    def __init__(self):
        MinLandIntegerPotentialField.__init__(self)
        
    def setup(self, driver, terrain):
        """ Initializes the field """
        MinLandIntegerPotentialField.setup(self, driver, terrain)
        
    def update(self):
        """ Updates this object """
        # just a simple implementation
        self.sources = self.driver.driver_enemy_hills[:]
        self.recalculate()

class UnchartedPotentialField(MinLandIntegerPotentialField):
    """ UnchartedPotentialField represents potential field where uncharted places has intensity value 0"""

    def __init__(self):
        MinLandIntegerPotentialField.__init__(self)
        
    def setup(self, driver, terrain):
        """ Initializes the field """
        MinLandIntegerPotentialField.setup(self, driver, terrain)
        
    def update(self):
        """ Updates this object """
        # just a simple implementation
        self.sources = [(row, col) for row in range(self.driver.rows) for col in range(self.driver.cols)
                if self.terrain.get_at((row,col)) == UNCHARTED]
        self.recalculate()

        
        
        
        
        
        
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
        
    def spread(self, sources, depth):
        """ Spreads the intensity from specified sources using distances of the sources. Assumes sources is empty """
        q = deque()
        for source in sources:
            self.set_at(source, 0)
            row, col = source
            self.sources[row][col].add(source)
            q.append(source)

        # Expand sources
        while len(q) > 0:
            loc = q.popleft()
            for to_spread in [pos for pos in self.driver.neighbours(loc)
                             if self.terrain.get_at(pos) == LAND]:
                if self.get_at(to_spread) == None:
                    self.set_at(to_spread, self.get_at(loc) + 1)
                    self.merge_sources(to_spread, self.get_at_sources(loc))
                    if self.get_at(to_spread) < depth:
                        q.append(to_spread)
                elif self.get_at(to_spread) == self.get_at(loc):
                    self.merge_sources(to_spread, self.get_at_sources(loc))
    
    def get_sources(self):
        return []
    
    def update(self, depth):
        self.sources = [[set() for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.field = [[None for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        self.spread(self.get_sources(), depth)

    def render_text_map(self):
        tmp = ''
        for row in range(self.driver.rows):
            tmp += '# '
            for col in range(self.driver.cols):
                val = self.get_at((row, col))
                if val == None:
                    tmp += '   ?   '
                else:
                    tmp += ' (%3i' % val
                    tmp += str(self.get_at_sources((row, col)))
                    tmp += ') '
            tmp += '\n'
        tmp += '\n'
        return tmp

    def get_potential(self, loc, none_value, poten_func):
        """ Computes potential on specified position in the field """
        if self.get_at(loc) == None:
            return none_value
        else:
            return poten_func(self.get_at(loc))
 
 
class FoodPotentialFieldWithSources(PotentialFieldWithSources):
    def __init__(self):
        PotentialFieldWithSources.__init__(self)
        
    def get_sources(self):
        return self.driver.food_list