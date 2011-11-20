#!/usr/bin/env python
from random import shuffle
from ants import *
                   
class Eskymo:

    destinations = []    
    directions = ['n','e','s','w']


    def __init__(self):
        pass

    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        pass

    def move(self, ants, ant_row, ant_col, directions):
        for direction in directions:
            (a_new_row, a_new_col) = ants.destination(ant_row, ant_col, direction)
            if (ants.unoccupied(a_new_row, a_new_col) and  not (a_new_row, a_new_col) in self.destinations):
                ants.issue_order((ant_row, ant_col, direction))    
                self.destinations.append((a_new_row, a_new_col))
                return
        shuffle(self.directions)
        for direction in self.directions:
            (a_new_row, a_new_col) = ants.destination(ant_row, ant_col, direction)
            if (ants.unoccupied(a_new_row, a_new_col) and  not (a_new_row, a_new_col) in self.destinations):
                ants.issue_order((ant_row, ant_col, direction))    
                self.destinations.append((a_new_row, a_new_col))
                return

    def go_to(self, ants, ant_row, ant_col, target_row, target_col):
        directions = ants.direction(ant_row, ant_col, target_row, target_col)
        shuffle(directions)
        self.move(ants, ant_row, ant_col, directions)
   

    def search_food(self, ants, ant_row, ant_col):
        closest_food = ants.closest_food(ant_row, ant_col)
        if (closest_food != None):
            self.go_to(ants, ant_row, ant_col, closest_food[0], closest_food[1])
        else:
            directions = ['n','e','s','w']
            shuffle(directions)                        
            self.move(ants, ant_row, ant_col, directions)


    def defend(self, ants, hill_row, hill_col, ant_row, ant_col):
        distance = ants.distance(ant_row,ant_col,hill_row, hill_col)
        if (distance == 1):
            return
        if (distance == 0):
            shuffle(self.directions)
            self.move(ants, ant_row, ant_col, self.directions)
        else:
            self.go_to(ants, ant_row, ant_col, hill_row, hill_col)
        
    def do_turn(self, ants):
        # reset
        self.destinations = []

        num_of_ants = len(ants.my_ants())
        num_of_defenders = min(num_of_ants / 2, 4)

        (my_hill_row, my_hill_col) = ants.my_hills()[0]

        num_of_attackers = 0
        (enemy_hill_row, enemy_hill_col) = (None, None)
        if (ants.enemy_hills() != []):
            ((enemy_hill_row, enemy_hill_col), owner) = min(ants.enemy_hills(), key=lambda hill: ants.distance(my_hill_row, my_hill_col, hill[0][0], hill[0][1])) #ants.enemy_hills()[0][0]
            num_of_attackers = max((num_of_ants - num_of_defenders) / 2 - 4, 0)

        sorted_ants = sorted(ants.my_ants(), key=lambda ant:ants.distance(ant[0],ant[1],my_hill_row, my_hill_col))
        defenders = sorted_ants[:num_of_defenders]

        if (num_of_attackers != 0):
            sorted_ants = sorted(sorted_ants[num_of_defenders:], key=lambda ant:ants.distance(ant[0],ant[1], enemy_hill_row, enemy_hill_col))
        else:
            sorted_ants = sorted_ants[num_of_defenders:]

        attackers = sorted_ants[:num_of_attackers]
        farmers = sorted_ants[num_of_attackers:]        

        for ant_row, ant_col in defenders:
            self.defend(ants, ant_row, ant_col, my_hill_row, my_hill_col)
        for ant_row, ant_col in attackers:
            self.go_to(ants, ant_row, ant_col, enemy_hill_row, enemy_hill_col)
        for ant_row, ant_col in farmers:
            self.search_food(ants, ant_row, ant_col)

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(Eskymo())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
