import numpy as np
import matplotlib.pyplot as plt
import functools
import math
import itertools
import time

global_r = (1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4)
global_c = 0

@functools.cache
def fact(n: int):
    """Computes the factorial of n

    :param n: input of the function
    :type n: int
    """
    return(math.factorial(n))

def draw_dices():
    """Draws 8 dices and gives the result in ascending order
    """
    dices = np.random.randint(0, 6, 8)
    return(dices2state(dices))

def dices2state(dices):
    """Transforms raw dice results into the usual representation 

    :param dices: Results of the dices
    :type dices: iterable(int)
    """
    temp = [0 for i in range(6)]
    for d in dices:
        temp[d] +=1
    rep = tuple(temp)
    return(rep)
    

@functools.cache
def proba(t : tuple, n : int):
    """Computes the probability of each state after drawing 8 dices

    :param t: state
    :type t: tuple
    :param n: number of dices
    :type n: int
    """
    if sum(t) != n:
        print("ERROR proba")
        return(0)

    rep = (fact(n)/(math.prod((fact(i) for i in t))))/(6**n)
    return(rep)

@functools.cache
def all_possible_dices_outputs(n : int):
    """Computes all possible dice outputs with n dice

    :param n: Number of dices available.
    :type n: int
    """
    def generate_tuples(sum_value, tuple_length):
        # Générer tous les tuples possibles
        possible_tuples = itertools.product(range(sum_value+1), repeat=tuple_length)
        
        # Filtrer les tuples dont la somme des éléments est égale à sum_value
        valid_tuples = [t for t in possible_tuples if sum(t) == sum_value]
        
        return valid_tuples

    return(generate_tuples(n, 6))

def rewardfun(score : int):
    if score < 21:
        return(global_c)
    elif score > 36:
        print(f"ERROR rewardfun {score}")
        raise RuntimeError
        return(0)
    else:
        return(global_r[score - 21])

@functools.cache
def strategy(dice_results : tuple, previous_choices : tuple, nb_available_dices : int, score : int):
    """Computes the optimal strategy

    :param dice_results: Results of the dice. dice_results[i] is the number of dice drawing i. O is a worm.
    :type dice_results: tuple
    :param previous_choices: Tells if a choice have already been made
    :type previous_choices: tuple
    :param nb_available_dices: Number of dices available
    :type nb_available_dices: int
    :param score: current_score
    :type score: int
    """
    reward = rewardfun(score) if previous_choices[0] == 1 else global_c
    choice = -1
    possible_choices = [i for i, x in enumerate(zip(dice_results, previous_choices)) if (x[0] != 0 and x[1] == 0)]

    for choice_temp in possible_choices:
        new_choices = list(previous_choices)
        new_choices[choice_temp] = 1
        new_choices = tuple(new_choices)
        new_score = score + choice_temp*dice_results[choice_temp]
        new_nb_available_dices = nb_available_dices - dice_results[choice_temp]
        reward_temp = sum(proba(dice_output, new_nb_available_dices) * strategy(dice_output, new_choices, new_nb_available_dices, new_score)[1]
                          for dice_output in all_possible_dices_outputs(new_nb_available_dices)
                          )
        if reward_temp > reward:
            reward = reward_temp
            choice = choice_temp
    return(choice, reward)
    


if __name__ == "__main__":
    
    
    x = 43
    print(bin(x))
    
    
    initial_throw = dices2state((1, 3, 3, 3, 4, 4, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, tuple(0 for i in range(6)), 8, 0))
    print(time.time() - tic)
    
    
    initial_throw = dices2state((1, 3, 3, 4, 4, 4, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, tuple(0 for i in range(6)), 8, 0))
    print(time.time() - tic)
    
    
    initial_throw = dices2state((1, 2, 3, 2, 4, 5, 5, 0))
    tic = time.time()
    print(strategy(initial_throw, tuple(0 for i in range(6)), 8, 0))
    print(time.time() - tic)
    
    initial_throw = dices2state((1, 2, 3, 2, 4, 5, 5, 5))
    tic = time.time()
    print(strategy(initial_throw, tuple(0 for i in range(6)), 8, 0))
    print(time.time() - tic)
    
    initial_throw = dices2state((5, 5, 5, 5, 5, 1, 5))
    tic = time.time()
    print(strategy(initial_throw, (1, 0, 0, 0, 0, 0), 7, 0))
    print(time.time() - tic)
    
    

