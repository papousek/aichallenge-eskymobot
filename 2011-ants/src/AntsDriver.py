from ants import *
from random import shuffle

try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint

class AntsDriver(Ants):

    def __init__(self):
        Ants.__init__(self)
        self.driver_destinations = []
        self.driver_my_hills = []
        self.driver_enemy_hills = []
        self.driver_last_moves = {}
        self.driver_current_moves = {}

    def all_enemy_hills(self):
        return self.driver_enemy_hills

    def all_my_hills(self):
        return self.driver_my_hills

    def closest(self, loc, loc_list, filter = None):
        min_dist = maxint
        closest_loc = None
        for item_loc in loc_list:
            if filter is None or item_loc not in filter:
                dist = self.distance(loc, item_loc)
                if dist < min_dist:
                    min_dist = dist
                    closest_loc = item_loc
        return closest_loc

    def closest_food(self, ant_loc, filter = None):
        return self.closest(ant_loc, self.food(), filter)    

    def finish_turn(self):
        Ants.finish_turn(self)
        self.driver_destinations = []
        self.driver_last_moves = self.driver_current_moves
        self.driver_current_moves = {}

    def issue_order(self, order):
        Ants.issue_order(self, order)
        self.driver_current_moves[self.destination(order[0], order[1])] = order[1]

    def move(self, ant_loc, direction):
        new_loc = self.destination(ant_loc, direction)
        if (self.unoccupied(new_loc) and not (new_loc in self.driver_destinations)):
            self.driver_destinations.append(new_loc)
            self.issue_order((ant_loc, direction))
            return True
        else:
            return False

    def move_random(self, ant_loc, directions = ['n','e','s','w'], use_last_move = False):
        if (use_last_move and ant_loc in self.driver_last_moves.keys()):
            preferred_direction = self.driver_last_moves[ant_loc]
            if (self.move(ant_loc, preferred_direction)):
                return True
        shuffle(directions)
        for direction in directions:
            if (self.move(ant_loc, direction)):
                return True
        return False

    def move_to(self, ant_loc, target_loc):
        target_directions = self.direction(ant_loc, target_loc)
        if (not self.move_random(ant_loc, target_directions)):
            self.move_random(ant_loc)

    def update(self, map_data):
        Ants.update(self, map_data)
        self.driver_my_hills = self.update_hills(self.driver_my_hills, self.my_hills())
        visible_enemy_hills = map(lambda x: x[0], self.enemy_hills())
        self.driver_enemy_hills = self.update_hills(self.driver_enemy_hills, visible_enemy_hills) 

    def update_hills(self, old_hills, visible_hills):
        tmp_hills = []
        for hill_loc in old_hills:
            if (self.visible(hill_loc) and not hill_loc in visible_hills):
                continue
            tmp_hills.append(hill_loc)
        for hill_loc in visible_hills:
            if (not hill_loc in tmp_hills):
                tmp_hills.append(hill_loc)
        return tmp_hills
    
    def neighbours(self, loc):
        return [self.destination(loc, dir) for dir in ['n','e','s','w']]
        
