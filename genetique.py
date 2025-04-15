from players import *
from game import * 
import numpy as np
import math
import matplotlib.pyplot as plt

N_PLAYERS = 5
N_EPOCH = 10
N_GAME_SIMU = 50

SURVIVAL_RATE = 1

N_DICE = 4
DOMINO_MIN = 11
DOMINO_MAX = 18
R = [1, 1, 2, 2, 3, 3, 4, 4]

PERCENTILES = [10,30, 50, 70, 90]




PERCENTILES = [10,30, 50, 70, 90]

if __name__ == "__main__":
    percentiles_evol = [[] for i in range(len(PERCENTILES)+2)]
    N_survival = math.floor(SURVIVAL_RATE*N_PLAYERS) - 1
    player11 = PlayerAB(N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R)
    player11.set_ab(1, 1)
    bestab = (1, 1)
    best_eval =  0
    #init the population
    population = [PlayerAB(N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R) for i in range(N_PLAYERS)]
    for i in range(N_PLAYERS):
        a = np.random.uniform(0, 2)
        b = np.random.uniform(0, 2)
        population[i].set_ab(a, b)
    
    tic = time.time()
    for epoch in range(N_EPOCH):
        print(f"EPOCH: {epoch +1} /{N_EPOCH}")
        #Evaluation
        evals = [0]*N_PLAYERS
        for player_idx, player in enumerate(population):
            game = Game(player, player11, N_dice=N_DICE, domino_min=DOMINO_MIN,domino_max=DOMINO_MAX,r=R)
            average_score = 0
            for i in range(N_GAME_SIMU):
                game.reinit()
                game.play_game(display=False)
                average_score += game.score('A') - game.score('B')
            average_score = average_score / N_GAME_SIMU
            evals[player_idx] = average_score
            player.eval = average_score
        
        if evals[0] > best_eval:
            best_eval = evals[0]
            bestab = (population[0].alpha, population[0].beta)
        # Selection and reproduction
        """
        population = sorted(population, key= lambda x: x.eval, reverse = True)
        evals = sorted(evals, reverse=True)
        babies_idx = list(range(N_survival, N_PLAYERS))
        for i,idx in enumerate(babies_idx[:-2]):
            parent_idx = i % N_survival
            a = population[parent_idx].alpha
            b = population[parent_idx].beta
            population[idx].set_ab(a, b)
        
        population[-1].set_ab(bestab[0], bestab[1])
        print(f"Best Alpha, Beta: {bestab}, eval: {evals[0]}")
        
        percentiles_evol[0].append(min(evals))
        percentiles_evol[-1].append(max(evals))
        for i, percent in enumerate(PERCENTILES):
            percentiles_evol[i+1].append(np.percentile(evals, percent))
               
        # mutation
        
        for player in population[:-2]:
            a = player.alpha
            b = player.beta
            da = np.random.uniform(-0.2,  0.2)
            db = np.random.uniform(-0.2, 0.2)
            a = max(0, min(20, a + da))
            b = max(0, min(20, b + db))
            player.set_ab(a, b)
            player.reinit()
        """


    epochs = list(range(1, N_EPOCH +1))
    plt.plot(epochs, percentiles_evol[0], label =f"Worst player")
    for i,evol in enumerate(percentiles_evol[1:-2]):
        plt.plot(epochs, evol, label =f"top {PERCENTILES[i]}%")
    plt.plot(epochs, percentiles_evol[-1], label =f"Best player")
    plt.legend()
    plt.show()


            
    
    
    