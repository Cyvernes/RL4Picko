import functools
import math
import numpy as np
import itertools
N_FACES = 6

@functools.cache
def fact(n: int):
    """Computes the factorial of n

    :param n: input of the function
    :type n: int
    """
    return(math.factorial(n))



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

def draw_dice(n = 8):
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