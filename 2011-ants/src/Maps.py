from ants import WATER, LAND

UNCHARTED = -5

#TODO Find a better way to process data in Terrain.update

class Terrain:
    """ Terrain represents a map with water and land and additional information
    about uncharted fields """
    
    def __init__(self):
        self.map = None
        self.driver = None
    
    def setup(self, driver):
        self.driver = driver
        self.map = [[UNCHARTED for col in range(self.driver.cols)]
                    for row in range(self.driver.rows)]
                    
    def update(self):
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
                    self.map[r][c] = LAND
        
    def get_at(self, (row, col)):
        return self.map[row][col]

    def render_text_map(self):
        tmp = ''
        terrain_render = {LAND: '.', WATER: '#', UNCHARTED: '?'}
        for row in self.map:
            tmp += '# %s\n' % ''.join([terrain_render[col] for col in row])
        return tmp
        