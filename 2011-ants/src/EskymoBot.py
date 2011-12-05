from AntsDriver import *
from Maps import Terrain
from Fields import *

            #1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(10 - x, 0) / 10.0) + \
            #0.2 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: max(30 - x, 0) / 30.0) +\
            #0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: max(200 - x, 0) / 200.0)
            #0.0 * self.food_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            #0.2 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            #0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x)

class EskymoBot:

    def __init__(self):
        self.terrain = Terrain()
        self.enemy_hill_potential_field = EnemyHillPotentialField()
        self.uncharted_potential_field = UnchartedPotentialField()
        self.food_potential_field = FoodPotentialFieldWithSources()
        self.not_visible_charted_potential_field = NotVisibleChartedPotentialField()

    def do_setup(self, driver):
        self.driver = driver
        self.terrain.setup(self.driver)
        self.food_potential_field.setup(self.driver, self.terrain)
        self.enemy_hill_potential_field.setup(self.driver, self.terrain)
        self.uncharted_potential_field.setup(self.driver, self.terrain)
#        self.not_visible_charted_potential_field.setup(self.driver, self.terrain)
    
    def compute_farmer_potential(self, loc):
        """ Computes total potential on specified location on the map for farmers """
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            0.2 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x)

    def compute_scouter_potential(self, loc):
        """ Computes total potential on specified location on the map for attackes """
        return \
            0.0 * self.food_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            2.0 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            1.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) #+ \
#            0.5 * self.not_visible_charted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x)

    def compute_attacker_potential(self, loc):
        """ Computes total potential on specified location on the map for attackes """
        return \
            0.0 * self.food_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            0.00 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            1.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.95 ** x)
        
    def attack(self, ants):
        for ant_loc in ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_attacker_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                if self.driver.move(ant_loc, direction):
                    self.driver.log("ANT " + str(ant_loc) + " MOVED TO " + direction + " WITH POTENTIAL " + str(potential))
                    break
    
    def defend(self, ants, hill_loc):
        for ant_loc in ants:
            distance = self.driver.distance(ant_loc, hill_loc)
            if (distance == 1):
                continue
            if (distance == 0):
                self.driver.move_random(ant_loc)
            else:
                self.driver.move_to(ant_loc, hill_loc)

    def farm(self, ants):
        lost_ants = []
        food_key_function = lambda ant: self.food_potential_field.get_potential(ant, maxint, lambda x: x)
        sorted_ants = sorted(ants, key = food_key_function)
        hunted_food = []
        for ant in sorted_ants:
            if (food_key_function(ant) == maxint):
                lost_ants.append(ant)
            else:
                possibilities = self.food_potential_field.get_at_sources(ant).difference(hunted_food)
                if (len(possibilities) == 0):
                    lost_ants.append(ant)
                else:
                    my_target_source = possibilities.pop()
                    my_distance = self.food_potential_field.get_potential(ant, maxint, lambda x:x)
                    for direction in [self.driver.direction(ant, pos).pop() for pos in self.driver.neighbours(ant) if my_target_source in self.food_potential_field.get_at_sources(pos) and my_distance > self.food_potential_field.get_potential(pos, maxint, lambda x:x)]:
                        if (self.driver.move(ant, direction)):
                            hunted_food.append(my_target_source)
                            break
                    else:
                        lost_ants.append(ant)

        sorted_lost_ants = sorted(lost_ants, key = lambda ant_loc: - self.compute_scouter_potential(ant_loc))

        for ant_loc in sorted_lost_ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_scouter_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                if self.compute_scouter_potential(ant_loc) > potential:
                    break
                if self.driver.move(ant_loc, direction):
                    break
            else:
                self.driver.move_random(ant_loc, ['n','e','s','w'], True)

    def max_number_of_defenders(self, hill_loc):
        result = 0
        for direction in ['n','e','s','w']:
            neigh_loc = self.driver.destination(hill_loc, direction)
            if (self.driver.passable(neigh_loc)):
                result = result + 1
        return result
    
    def do_turn(self):
        # update attributes
        self.terrain.update()
        self.food_potential_field.update(20)
        self.enemy_hill_potential_field.update(20)
        self.uncharted_potential_field.update(100)
        # available ants
        ants = self.driver.my_ants()
        num_of_ants = len(ants)
        num_of_my_hills = len(self.driver.all_my_hills())
        num_of_enemy_hills = len(self.driver.all_enemy_hills())
        num_of_defenders_sum = 0
        num_of_attackers_sum = 0
        # defenders
        for hill_loc in self.driver.all_my_hills():
            num_of_defenders = min(num_of_ants / (num_of_my_hills+1), self.max_number_of_defenders(hill_loc))
            ants = sorted(ants, key=lambda ant: self.driver.distance(ant,hill_loc))
            defenders = ants[:num_of_defenders]
            ants = ants[num_of_defenders:]
            self.defend(defenders, hill_loc)
            num_of_defenders_sum = num_of_defenders_sum + num_of_defenders
        # attackers
        ants = sorted(ants, key=lambda ant:self.compute_attacker_potential(ant))
        num_of_attackers_max = ((num_of_ants - num_of_defenders_sum) / 3) * min(num_of_enemy_hills, 1)
        while num_of_attackers_sum < num_of_attackers_max and self.compute_attacker_potential(ants[num_of_attackers_sum]):
            num_of_attackers_sum = num_of_attackers_sum + 1
        attackers = ants[:num_of_attackers_sum]
        ants = ants[num_of_attackers_sum:]
        self.attack(attackers)
        # farmers
        farmers = ants
        self.farm(farmers)

