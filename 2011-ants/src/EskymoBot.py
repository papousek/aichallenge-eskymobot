from AntsDriver import *
from Maps import Terrain, MapWithAnts
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
        self.map_with_ants = MapWithAnts()
        self.enemy_hill_potential_field = EnemyHillPotentialField()
        self.uncharted_potential_field = UnchartedPotentialField()
        self.food_potential_field = FoodPotentialField()
        self.fog_potential_field = FogPotentialField()
        self.ally_potential_field = AllyPotentialField()

    def do_setup(self, driver):
        self.driver = driver
        self.terrain.setup(self.driver)
        self.map_with_ants.setup(self.driver, self.terrain)
        self.food_potential_field.setup(self.driver, self.terrain)
        self.enemy_hill_potential_field.setup(self.driver, self.terrain)
        self.uncharted_potential_field.setup(self.driver, self.terrain)
        self.fog_potential_field.setup(self.driver, self.terrain)
        self.ally_potential_field.setup(self.driver, self.terrain)
    
    def try_to_move_ant(self, ant_loc, direction):
        """ Basically, this method has the same purpose as AntsDriver.move, but should behave better """
        new_loc = self.driver.destination(ant_loc, direction)
        if not self.map_with_ants.get_at(new_loc):
            self.map_with_ants.remove_ant(ant_loc)
            self.map_with_ants.place_ant(new_loc)
            self.driver.issue_order((ant_loc, direction))
            return True
        else:
            return False
    
    def compute_farmer_potential(self, loc):
        """ Computes total potential on specified location on the map for farmers """
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(1, 1313 * (1.5 ** (-x)))) + \
            1.0 * self.uncharted_potential_field.get_potential(loc, -1000, lambda x: -x) + \
            0.0 * self.fog_potential_field.get_potential(loc, 0, lambda x: max(9, 25 * (1.1 ** (-x)))) + \
            0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: max(200 - x, 0) / 200.0)

    def compute_attacker_potential(self, loc):
        """ Computes total potential on specified location on the map for attackes """
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(1, 1313 * (1.5 ** (-x)))) + \
            1.0 * self.uncharted_potential_field.get_potential(loc, -1000, lambda x: -x) + \
            0.0 * self.fog_potential_field.get_potential(loc, 0, lambda x: max(9, 25 * (1.1 ** (-x)))) + \
            10.0 * self.enemy_hill_potential_field.get_potential(loc, -10000000, lambda x: -1000 * x)
        
    def attack(self, ants, hill_loc):
        for ant_loc in ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_attacker_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                if self.try_to_move_ant(ant_loc, direction):
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
        for ant_loc in ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_farmer_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                if self.try_to_move_ant(ant_loc, direction):
                    break

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
        self.map_with_ants.update()
        self.food_potential_field.update()
        self.enemy_hill_potential_field.update()
        self.uncharted_potential_field.update()
        self.fog_potential_field.update()
        self.ally_potential_field.update()
        #self.driver.log(self.map_with_ants.render_text_map())
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
        num_of_attackers = len(self.driver.all_enemy_hills()) * max((num_of_ants - num_of_defenders_sum) / (num_of_enemy_hills + 1) - 4, 0)
        ants = sorted(ants, key = lambda ant : -self.compute_attacker_potential(ant))
        attackers = ants[:num_of_attackers]
        ants = ants[num_of_attackers:]
        self.attack(attackers, hill_loc)
        num_of_attackers_sum = num_of_attackers_sum + num_of_attackers
        # farmers
        farmers = sorted(ants, key = lambda ant: -self.compute_farmer_potential(ant))
        self.farm(farmers)
