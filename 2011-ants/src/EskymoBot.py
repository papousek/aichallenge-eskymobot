from AntsDriver import *
                   
class EskymoBot:

    def __init__(self):
        pass

    def do_setup(self, driver):
        self.driver = driver
        pass
    
    def attack(self, ants, hill_loc):
        for ant_loc in ants:
            self.driver.move_to(ant_loc, hill_loc)
    
    def defend(self, ants, hill_loc):
        for ant_loc in ants:
            distance = self.driver.distance(ant_loc, hill_loc)
            if (distance == 1):
                continue
            if (distance == 0):
                self.driver.move_random(ant_loc)
            else:
                self.driver.move_to(ant_loc, hill_loc)

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
        self.random_walk(farmers)
