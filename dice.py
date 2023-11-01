import numpy as np
import matplotlib.pyplot as plt
import functools
import math
import itertools
import time

N_DICE = 8
N_FACES = 6
DOMINO_MIN = 21
DOMINO_MAX = 36

global_c = 0
global_r = [global_c for _ in range(DOMINO_MIN)]+[1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]

@functools.cache
def fact(n: int):
    """Computes the factorial of n

    :param n: input of the function
    :type n: int
    """
    return(math.factorial(n))

def draw_dice(n = N_DICE):
    """Draws N dice and gives the result in ascending order
    """
    dice = np.random.randint(0, N_FACES, n)
    return(dice2state(dice))

def dice2state(dice):
    """Transforms raw dice results into the usual representation 

    :param dice: Results of the dice
    :type dice: iterable(int)
    """
    temp = [0 for i in range(N_FACES)]
    for d in dice:
        temp[d] +=1
    rep = tuple(temp)
    return(rep)
    

@functools.cache
def proba(t : tuple, n : int):
    """Computes the probability of each state after drawing N dice

    :param t: state
    :type t: tuple
    :param n: number of dice
    :type n: int
    """
    if sum(t) != n:
        print("ERROR proba")
        return(0)

    rep = (fact(n)/(math.prod((fact(i) for i in t))))/(N_FACES**n)
    return(rep)

@functools.cache
def all_possible_dice_outputs(n : int):
    """Computes all possible dice outputs with n dice

    :param n: Number of dice available.
    :type n: int
    """
    def generate_tuples(sum_value, tuple_length):
        # Générer tous les tuples possibles
        possible_tuples = itertools.product(range(sum_value+1), repeat=tuple_length)
        
        # Filtrer les tuples dont la somme des éléments est égale à sum_value (ie le nombre de dés à lancer)
        valid_tuples = [t for t in possible_tuples if sum(t) == sum_value]
        
        return valid_tuples

    return(generate_tuples(n, N_FACES))

def rewardfun(score : int):
    if score > DOMINO_MAX:
        return(global_r[DOMINO_MAX])
    else:
        return(global_r[score])

@functools.cache
def strategy(dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int):
    """Computes the optimal strategy
    Idée:
    On peut surement améliorer en mémoisant (dans une fonction interne) sans dice result. 
    Car on choisit l'action a prendre sur l'espérance sur le lancé de dé. On peut donc mémoiser cette espérance pour ne pas à avoir a sommer à chaque fois

    :param dice_results: Results of the dice. dice_results[i] is the number of dice drawing i. 0 is a worm.
    :type dice_results: tuple
    :param previous_choices: Tells if a choice has already been made
    :type previous_choices: int
    :param nb_available_dice: Number of dice available
    :type nb_available_dice: int
    :param score: current_score
    :type score: int
    """
    reward = rewardfun(score) if previous_choices % 2 == 1 else global_c
    choice = -1
    possible_choices = [i for i in range(len(dice_results)) if dice_results[i] != 0 and ((previous_choices >> i) & 1) == 0]
    for choice_temp in possible_choices:
        new_choices = previous_choices | (1 << choice_temp)
        dice_value = 5 if choice_temp == 0 else choice_temp
        new_score = score + dice_value*dice_results[choice_temp]
        new_nb_available_dice = nb_available_dice - dice_results[choice_temp]
        reward_temp = sum(
                            proba(dice_output, new_nb_available_dice) 
                          * strategy(dice_output, new_choices, new_nb_available_dice, new_score)[1]
                          for dice_output in all_possible_dice_outputs(new_nb_available_dice)
                          )
        if reward_temp > reward:
            reward = reward_temp
            choice = choice_temp
    return(choice, reward)

if __name__ == "__main__":
    
    
    initial_throw = dice2state((1, 3, 3, 3, 4, 4, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, 0, N_DICE, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 3, 4, 5, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, 0, N_DICE, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 3, 5, 5, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, 0, N_DICE, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 5, 5, 5, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, 0, N_DICE, 0))
    print(time.time() - tic)
