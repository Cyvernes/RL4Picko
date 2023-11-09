from players import *
from game import * 
import numpy as np
import math


N_PLAYERS = 20
N_EPOCH = 10
N_GAME_SIMU = 5

SURVIVAL_RATE = 0.4

N_DICE = 4
DOMINO_MIN = 11
DOMINO_MAX = 18
R = [1, 1, 2, 2, 3, 3, 4, 4]

PERCENTILES = [10,30, 50, 70, 90]


if __name__ == "__main__":
    percentiles_evol = [[]]*(len(PERCENTILES))
    N_survival = math.floor(SURVIVAL_RATE*N_PLAYERS) - 1
    player11 = PlayerAB(N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R)
    player11.set_ab(1, 1)
    
    #init the population
    population = [PlayerAB(N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R) for i in range(N_PLAYERS)]
    for i in range(N_PLAYERS):
        a,b = np.random.uniform(0, 2), np.random.uniform(0, 2)
        population[i].set_ab(a, b)
    
    tic = time.time()
    for epoch in range(N_EPOCH):
        #Evaluation
        evals = [0]*N_PLAYERS
        for player_idx, player in enumerate(population):
            game = Game(player, player11, N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R)
            average_score = 0
            for i in range(N_GAME_SIMU):
                game.reinit()
                game.play_game(display=False)
                average_score += game.score('A')
            average_score = average_score / N_GAME_SIMU
            evals[player_idx] = average_score
            
        # Selection and reproduction
        sorting_list = sorted(zip(evals, population), key=lambda x: x[0], reverse=True)
        population = [x for _, x in sorting_list]
        evals = [x for x, _ in sorting_list]
        babies_idx = list(range(N_survival, N_PLAYERS))
        for i,idx in enumerate(babies_idx):
            parent_idx = i % N_survival
            a = population[parent_idx].alpha
            b = population[parent_idx].beta
            population[idx].set_ab(a, b)
        print(np.mean(evals))
        # mutation
        for player in population:
            a = player.alpha
            b = player.beta
            da, db = np.random.uniform(-0.05, 0.05), np.random.uniform(-0.05, 0.05)
            a = max(0,min(2, a + da))
            b = max(0,min(2, b + db))
            player.set_ab(a, b)



            
    
    
    