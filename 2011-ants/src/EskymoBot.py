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

    def do_setup(self, driver):
        self.driver = driver
        self.terrain.setup(self.driver)
        self.food_potential_field.setup(self.driver, self.terrain)
        self.enemy_hill_potential_field.setup(self.driver, self.terrain)
        self.uncharted_potential_field.setup(self.driver, self.terrain)
    
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
            1.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x)

    def compute_attacker_potential(self, loc):
        """ Computes total potential on specified location on the map for attackes """
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            0.05 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 0.5 ** x) + \
            10.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: 0.95 ** x)
        
    def attack(self, ants, hill_loc):
        for ant_loc in ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_attacker_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            if self.driver.move(ant_loc, direction):
                for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
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

        sorted_lost_ants = sorted(lost_ants, key = lambda ant_loc: self.compute_scouter_potential(ant_loc))

        for ant_loc in sorted_lost_ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_scouter_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                if self.driver.move(ant_loc, direction):
                    break
                
#        for ant_loc in ants:
#            # For all four possible ways get the potential from potential map
#            potentials = [(direction, self.compute_farmer_potential(self.driver.destination(ant_loc, direction)))
#                    for direction in ['n','e','s','w']]
#            # Find the best way to move (preferably the one with the greatest potential)
#            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
#                if self.driver.move(ant_loc, direction):
#                    break

    def max_number_of_defenders(self, hill_loc):
        result = 0
        for direction in ['n','e','s','w']:
            neigh_loc = self.driver.destination(hill_loc, direction)
            if (self.driver.passable(neigh_loc)):
                result = result + 1
        return result

    def random_walk(self, ants):
        hunted_food = []
        # with food
        while(ants != []):
            ant_loc = None
            closest_food = None
            distance = None
            for current_ant_loc in ants:
                current_closest_food = self.driver.closest_food(current_ant_loc, hunted_food)
                if (current_closest_food == None):
                    continue
                current_distance = self.driver.distance(current_ant_loc, current_closest_food)
                if (closest_food == None or distance > current_distance):
                    ant_loc = current_ant_loc
                    closest_food = current_closest_food
                    distance = current_distance
                    continue
            if (closest_food == None):
                break
            ants.remove(ant_loc)
            hunted_food.append(closest_food)                
            self.driver.move_to(ant_loc, closest_food)            
        # without food                        
        for ant_loc in ants:
            use_last_move = True
            if (random.randint(1,100) > 90):
                use_last_move = False
            self.driver.move_random(ant_loc, ['n','e','s','w'], use_last_move)
    
    def do_turn(self):
        # update attributes
        self.terrain.update()
        self.food_potential_field.update(10)
        self.enemy_hill_potential_field.update()
        self.uncharted_potential_field.update()
        self.driver.log(self.food_potential_field.render_text_map())
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
            ants = sorted(ants, key=lambda ant:self.driver.distance(ant,hill_loc))
            defenders = ants[:num_of_defenders]
            ants = ants[num_of_defenders:]
            self.defend(defenders, hill_loc)
            num_of_defenders_sum = num_of_defenders_sum + num_of_defenders
        # attackers
        for hill_loc in self.driver.all_enemy_hills():
            num_of_attackers = max((num_of_ants - num_of_defenders_sum) / (num_of_enemy_hills + 1) - 4, 0)
            ants = sorted(ants, key=lambda ant:self.driver.distance(ant,hill_loc))
            attackers = ants[:num_of_attackers]
            ants = ants[num_of_attackers:]
            self.attack(attackers, hill_loc)
            num_of_attackers_sum = num_of_attackers_sum + num_of_attackers
        # farmers
        farmers = ants
        self.farm(farmers)
