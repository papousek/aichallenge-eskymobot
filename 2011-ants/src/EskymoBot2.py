from AntsDriver import *
                   
class EskymoBot:

    def __init__(self):
        pass

    def do_setup(self, driver):
        self.driver = driver
        pass
    
    def attack(self, ants, hill):
        pass
    
    def defend(self, ants, hill_loc):
        for ant_loc in ants:
            distance = self.driver.distance(ant_loc, hill_loc)
            if (distance == 1):
                continue
            if (distance == 0):
                self.driver.move_random(ant_loc)
            else:
                self.driver.move_to(ant_loc, hill_loc)

    def random_walk(self, ants):
        hunted_food = []
        """
        while (ants != []):
            ant_loc = min(ants, key=lambda ant:self.driver.distance(ant, self.driver.closest_food(ant, hunted_food)))
            ants.remove(ant_loc)
            closest_food = self.driver.closest_food(ant_loc)
            if (closest_food == None):
                break
            hunted_food.append(closest_food)                
            self.driver.move_to(ant_loc, closest_food)
        for ant_loc in ants:
            self.driver.move_random(ant_loc)
        """            
        for ant_loc in ants:
            self.driver.move_to(ant_loc, (2,10))
#            closest_food = self.driver.closest_food(ant_loc, hunted_food)
#            if (closest_food != None):
#                hunted_food.append(closest_food)
#                self.driver.move_to(ant_loc, closest_food)
#            else:
#                self.driver.move_random(ant_loc)
                

    def do_turn(self):
        # available ants
        ants = self.driver.my_ants()
        num_of_ants = len(ants)
        # defenders
#        num_of_defenders = num_of_defenders = min(num_of_ants / 2, 4 * len(self.driver.all_my_hills()))
        """
        for hill_loc in self.driver.all_my_hills():
            ants = sorted(ants, key=lambda ant:self.driver.distance(ant,hill_loc))
            defenders = ants[:num_of_defenders]
            ants = ants[num_of_defenders:]
            self.defend(defenders, hill_loc)
        """
        # farmers
        farmers = ants
        self.random_walk(farmers)
