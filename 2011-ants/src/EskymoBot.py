from AntsDriver import *
from Maps import Terrain, MapWithAnts
from Fields import *

class EskymoBot:

    def __init__(self):
        self.terrain = Terrain()
        self.map_with_ants = MapWithAnts()
        self.enemy_hill_potential_field = EnemyHillPotentialField()
        self.uncharted_potential_field = UnchartedPotentialField()
        self.food_potential_field = FoodPotentialFieldWithSources()
        self.fog_potential_field = FogPotentialField()

    def do_setup(self, driver):
        self.driver = driver
        self.terrain.setup(self.driver)
        self.map_with_ants.setup(self.driver, self.terrain)
        self.food_potential_field.setup(self.driver, self.terrain)
        self.enemy_hill_potential_field.setup(self.driver, self.terrain)
        self.uncharted_potential_field.setup(self.driver, self.terrain)
        self.fog_potential_field.setup(self.driver, self.terrain)
        self.attackradius2_plus_one = int((sqrt(self.driver.attackradius2) + 1.0) ** 2.0)
        self.attackradius2_plus_two = int((sqrt(self.driver.attackradius2) + 2.0) ** 2.0)
    
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

    def move_random(self, ant_loc, directions = None):
        #self.driver.move_random(ant_loc)
        if directions == None:
            directions = ['n','e','s','w']
        shuffle(directions)
        for direction in directions:
            if (self.try_to_move_ant(ant_loc, direction)):
                return True
        return False
    
    def move_to(self, ant_loc, target_loc):
        #self.driver.move_to(ant_loc, hill_loc)
        target_directions = self.driver.direction(ant_loc, target_loc)
        if (not self.move_random(ant_loc, target_directions)):
            self.move_random(ant_loc)

    def compute_allies(self, loc, player, radius2):
        """ Returns list of allied ants of specified player surrounding specified field """
        return filter(lambda (ant_loc, owner): owner == player and self.driver.radius2(loc, ant_loc) <= radius2, self.driver.ant_list.items())

    def compute_enemies(self, loc, player, radius2):
        """ Returns list of enemy ants of specified player surrounding specified field """
        return filter(lambda (ant_loc, owner): owner != player and self.driver.radius2(loc, ant_loc) <= radius2, self.driver.ant_list.items())

    def compute_farmer_potential(self, loc):
        """ Computes total potential on specified location on the map for farmers """
        return \
            0.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(1, 1313 * (1.5 ** (-x)))) + \
            1.0 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 400 * (1.2 ** (-x))) + \
            0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: max(200 - x, 0) / 200.0)

    def compute_scouter_potential(self, loc):
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(1, 1313 * (1.5 ** (-x)))) + \
            1.0 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 400 * (1.2 ** (-x))) + \
            0.0 * self.enemy_hill_potential_field.get_potential(loc, 0, lambda x: max(200 - x, 0) / 200.0)    

    def compute_attacker_potential(self, loc):
        """ Computes total potential on specified location on the map for attackes """
        return \
            1.0 * self.food_potential_field.get_potential(loc, 0, lambda x: max(1, 1313 * (1.5 ** (-x)))) + \
            1.0 * self.uncharted_potential_field.get_potential(loc, 0, lambda x: 400 * (1.2 ** (-x))) + \
            10.0 * self.enemy_hill_potential_field.get_potential(loc, 10000000, lambda x: -1000 * x)
        
    def attack(self, ants, hill_loc):
        for ant_loc in ants:
            # For all four possible ways get the potential from potential map
            potentials = [(direction, self.compute_attacker_potential(self.driver.destination(ant_loc, direction)))
                    for direction in ['n','e','s','w']]
            # Find the best way to move (preferably the one with the greatest potential)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                enemy_ants = self.compute_enemies(self.driver.destination(ant_loc, direction), 0, self.attackradius2_plus_one)
                enemies = reduce(lambda x,y:min(x,y), filter(lambda x: x > 0, [len(self.compute_enemies(loc, owner, self.attackradius2_plus_two)) for (loc, owner) in enemy_ants]), 100)
                if (len(enemy_ants) == 0 or len(enemy_ants) < enemies) and self.try_to_move_ant(ant_loc, direction):
                    break
    
    def defend(self, ants, hill_loc):
        for ant_loc in ants:
            distance = self.driver.distance(ant_loc, hill_loc)
            if (distance == 1):
                continue
            if (distance == 0):
                self.move_random(ant_loc)
            else:
                self.move_to(ant_loc, hill_loc)

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
                    for direction, pos in [(self.driver.direction(ant, pos).pop(), pos) for pos in self.driver.neighbours(ant) if my_target_source in self.food_potential_field.get_at_sources(pos) and my_distance > self.food_potential_field.get_potential(pos, maxint, lambda x:x)]:
                        enemy_ants = self.compute_enemies(self.driver.destination(ant, direction), 0, self.attackradius2_plus_one)
                        enemies = reduce(lambda x,y:min(x,y), filter(lambda x: x > 0, [len(self.compute_enemies(loc, owner, self.attackradius2_plus_two)) for (loc, owner) in enemy_ants]), 100)
                        if (len(enemy_ants) == 0 or len(enemy_ants) < enemies) and self.try_to_move_ant(ant, direction):
                            hunted_food.append(my_target_source)
                            break
                    else:
                        lost_ants.append(ant)

        sorted_lost_ants = sorted(lost_ants, key = lambda ant_loc: - self.compute_scouter_potential(ant_loc))

        for ant_loc in sorted_lost_ants:
            # For all four possible ways get the potential from potential map
            directions = ['n','e','s','w']
            potentials = [(direction, self.compute_scouter_potential(self.driver.destination(ant_loc, direction)))
                    for direction in directions]
            # Find the best way to move (preferably the one with the greatest potential)
            shuffle(potentials)
            for direction, potential in sorted(potentials, key = lambda (d1, p1): -p1):
                enemy_ants = self.compute_enemies(self.driver.destination(ant_loc, direction), 0, self.attackradius2_plus_one)
                enemies = reduce(lambda x,y:min(x,y), filter(lambda x: x > 0, [len(self.compute_enemies(loc, owner, self.attackradius2_plus_two)) for (loc, owner) in enemy_ants]), 100)
                if (len(enemy_ants) == 0 or len(enemy_ants) < enemies) and self.try_to_move_ant(ant_loc, direction):
                    break 

    def max_number_of_defenders(self, hill_loc):
        result = 0
        for direction in ['n','e','s','w']:
            neigh_loc = self.driver.destination(hill_loc, direction)
            if (self.driver.passable(neigh_loc)):
                result = result + 1
        return result

    def __random_walk(self, ants):
        # this function is (maybe) no more needed
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
        pre_t = self.driver.time_remaining()
        self.terrain.update()
        pre_mwa = self.driver.time_remaining()
        self.map_with_ants.update()
        pre_fpf = self.driver.time_remaining()
        self.food_potential_field.update(10)
        pre_ehpf = self.driver.time_remaining()
        self.enemy_hill_potential_field.update()
        pre_upf = self.driver.time_remaining()
        self.uncharted_potential_field.update()
        pre_upfg = self.driver.time_remaining()
        self.fog_potential_field.update(20)
        pre_ants = self.driver.time_remaining()
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
        post_ants = self.driver.time_remaining()
        if False:
            self.driver.log("Terrain: " + str(-(pre_mwa - pre_t)) +
                ", Map With Ants: " + str(-(pre_fpf - pre_mwa)) +
                ", Food Field: " + str(-(pre_ehpf - pre_fpf)) +
                ", Enemy Hill: " + str(-(pre_upf - pre_ehpf)) +
                ", Uncharted: " + str(-(pre_upfg - pre_upf)) +
                ", Fog: " + str(-(pre_ants - pre_upfg)) +
                ", Movement: " + str(-(post_ants - pre_ants)))
        
