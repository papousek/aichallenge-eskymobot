from ants import WATER, LAND

UNCHARTED = -5

#TODO Find a better way to process data in Terrain.update

class Terrain:
    """ Terrain represents a map with water and land and additional information
    about uncharted fields """
    
    def __init__(self):
        self.map = None
        self.driver = None
        self.new_fields = []
    
    def setup(self, driver):
        self.driver = driver
        self.map = [[UNCHARTED for col in range(self.driver.cols)]
                    for row in range(self.driver.rows)]
                    
    def update(self):
        self.new_fields = []
        # if vision map is not ready, initialize it
        if (self.driver.vision == None):
            self.driver.visible((0, 0))
        
        # update information about water
        for r, rows in enumerate(self.driver.map):
            for c, data in enumerate(rows):
                if data == WATER:
                    self.map[r][c] = WATER

        # update information about uncharted fields
        for r, rows in enumerate(self.driver.vision):
            for c, data in enumerate(rows):
                if data and self.map[r][c] == UNCHARTED:
                    self.new_fields.append((r,c))
                    self.map[r][c] = LAND
        
    def get_at(self, (row, col)):
        return self.map[row][col]

    def render_text_map(self):
        tmp = ''
        terrain_render = {LAND: '.', WATER: '#', UNCHARTED: '?'}
        for row in self.map:
            tmp += '# %s\n' % ''.join([terrain_render[col] for col in row])
        return tmp

class MapWithAnts:
    """ Map with information about where ants and other barriers are. Suitable if a question whether there is
    an ant on specified location needs to run in constant time. """
    
    def __init__(self):
        self.map = None
        self.driver = None
        self.terrain = None
    
    def setup(self, driver, terrain):
        self.driver = driver
        self.terrain = terrain
        self.map = [[True for col in range(self.driver.cols)] for row in range(self.driver.rows)]
                    
    def update(self):
        self.map = [[self.terrain.get_at((row, col)) != LAND for col in range(self.driver.cols)] for row in range(self.driver.rows)]
        for loc in self.driver.food_list:
            self.place_ant(loc)
        for loc, owner in self.driver.ant_list.items():
            self.place_ant(loc)
        
    def remove_ant(self, (row, col)):
        self.map[row][col] = False

    def place_ant(self, (row, col)):
        self.map[row][col] = True

    def get_at(self, (row, col)):
        return self.map[row][col]
        
    def render_text_map(self):
        tmp = ''
        map_render = {True: 'O', False: '.'}
        for row in self.map:
            tmp += '# %s\n' % ''.join([map_render[col] for col in row])
        return tmp
 