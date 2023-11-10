import functools
import time
import logging
from tools import *
from typing import Tuple


class Player:
    
    def __init__(self, N_dice = 8, domino_min = 21, domino_max = 36, r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]) -> None:
        self.N_dice = N_dice
        self.N_faces = 6
        self.domino_min = domino_min
        self.domino_max = domino_max
        self.C = 0
        self.r = r
        self.basic_r = r
        self.dominos = []
        self.clear_cache = True
        self.eval = None

    def reinit(self) -> None:
        self.C = 0
        self.r = self.basic_r
        self.dominos = []

    def set_C(self, new_C: int):
        if self.clear_cache:
            logging.debug("cache clear")
            self.expectancy.cache_clear()
            #self.strategy.cache_clear()
        self.C = new_C

    def set_r(self, new_r: list[int]):
        if self.clear_cache:
            logging.debug("cache clear")
            self.expectancy.cache_clear()
            #self.strategy.cache_clear()
        self.r = new_r.copy()


    def rewardfun(self, score : int, previous_choices : int) -> int:
        if score < self.domino_min:
            return(-self.C)
        elif previous_choices % 2 == 1:
            return(max(self.r[:min(score - self.domino_min , self.domino_max - self.domino_min) + 1]))
        else:
            return(-self.C)

    def init_turn(self, grill: list[bool], r: list[int], dominos_adv: list[int]):
        """Initialises self.C and self.r according to game data

        :param grill: game grill
        :type grill: list[bool]
        :param r: dominos rewards
        :type r: list[int]
        :param top_domino_adv: domino in the top of the adversary's stack
        :type top_domino_adv: int
        """
        new_r = self.r.copy()
        for i,available in enumerate(grill):
            if not available:
                new_r[i] = -self.C
        self.set_r(new_r)
        logging.debug(f"Reward vector at this turn: {self.r}")


    def play_dice(self, dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int) -> int:
        """Do the choice when dice are drawn

        :param dice_results: Results of the dice given in counting format
        :type dice_results: tuple
        :param previous_choices: Previous choices made by the player encoded by the indicative function given by the bits of the int
        :type previous_choices: int
        :param nb_available_dice: number of available dice
        :type nb_available_dice: int
        :param score: score already achieved
        :type score: int
        :return: The dice selected by the player
        :rtype: int
        """
        choice, reward = self.strategy(dice_results, previous_choices, nb_available_dice, score)
        logging.info(f"chooses {choice} with reward {reward}")
        return(choice)
    
    def play_grill(self, grill, score : int) -> int:
        """Selects the domino according to the score and the grill

        :param grill: _description_
        :type grill: _type_
        :param score: _description_
        :type score: int
        :return: _description_
        :rtype: int
        """
        if score < self.domino_min:
            return(-1)
        domino = np.argmax(self.r[:score-self.domino_min+1]) + self.domino_min
        domino = domino if self.r[domino-self.domino_min] > 0 else -1
        return(domino)
    
    @functools.cache
    def expectancy(self, choices: int, nb_available_dice: int, score : int) -> float:
        """Returns the expected reward with the given situation

        :param choices: bit array of chosen dice
        :type choices: int
        :param nb_available_dice: number of available dice
        :type nb_available_dice: int
        :param score: score already achieved
        :type score: int
        :return: expected reward
        :rtype: float
        """
        return(sum(
                        proba(dice_output, nb_available_dice) 
                        * self.strategy(dice_output, choices, nb_available_dice, score)[1]
                    for dice_output in all_possible_dice_outputs(nb_available_dice)
                    )
               )
    
    
    #@functools.cache
    def strategy(self, dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int) -> Tuple[Tuple[int, int], int]:
        """Computes the optimal strategy using Bellman equation.

        :param dice_results: Results of the dice given in counting format
        :type dice_results: tuple
        :param previous_choices: Previous choices made by the player encoded by the indicative function given by the bits of the int
        :type previous_choices: int
        :param nb_available_dice: Number of dice available
        :type nb_available_dice: int
        :param score: Current score before taking an action
        :type score: int
        :return: (choice, expectancy).  choice = (chosen dice, 0 if player stops or 1 otherwise)
        :rtype: Tuple[Tuple[int, int], int]
        """

        #Test all possible choices
        possible_choices = [i for i, dr in enumerate(dice_results) if dr and( not ((previous_choices >> i) & 1))]
        if not possible_choices:#the round is failed
            return((None, -self.C))
        # select the choice that have the best expectancy
        reward_temp = float('-inf')
        choice_temp = (-1, -1)
        for choice in possible_choices: # all other possible choices
            #Compute previous_choices, score and nb_available_dice for the potential choice
            new_choices = previous_choices | (1 << choice)
            new_score = score + (choice if choice else 5)*dice_results[choice]
            new_nb_available_dice = nb_available_dice - dice_results[choice]
                
            #Compute the expected reward of the choice
            expected_reward_continuing = self.expectancy(new_choices, new_nb_available_dice, new_score) 
            if new_choices % 2 == 1 and self.rewardfun(new_score, new_choices) >= expected_reward_continuing: #The player should stop after chosing choice
                reward_by_stopping = self.rewardfun(new_score, new_choices)  
                reward = reward_by_stopping
                pchoice = (choice, 0)
            else:
                reward = expected_reward_continuing
                pchoice = (choice, 1)
                
            if reward >= reward_temp:
                reward_temp = reward
                choice_temp = pchoice
                
        return(choice_temp, reward_temp)

class PlayerAB(Player):

    def __init__(self, clear_cache = True, N_dice = 8, domino_min = 21, domino_max = 36, r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]) -> None:
        super().__init__(N_dice, domino_min, domino_max , r)
        self.alpha = 1
        self.beta = 1
        self.adv = (0,0) #(last domino of adversary, reward we get if the player steals it)
        self.clear_cache = clear_cache
    
    def set_ab(self, alpha: int, beta:int) -> None:
        self.alpha = alpha
        self.beta = beta
    
    def rewardfun(self, score : int , previous_choices : int) -> int:
        if previous_choices % 2 == 1:
            if score and score == self.adv[0]:# Stealing
                return self.adv[1]
            return super().rewardfun(score, previous_choices)
        else:
            return(-self.C)

    def init_turn(self, grill: list[bool], r: list[int], dominos_adv: list[int]):
        # init C
        if self.dominos:
            top_domino_me = self.dominos[-1]
            self.set_C(self.alpha*r[top_domino_me-self.domino_min])
        else:
            self.set_C(0)

        # init adv
        if dominos_adv:
            top_domino_adv = dominos_adv[-1]
            r_adv = r[top_domino_adv-self.domino_min]
            self.adv = (top_domino_adv, 2*r_adv*self.beta)
        else:
            self.adv = (0,0)

        super().init_turn(grill, r, dominos_adv)
    
    def play_grill(self, grill, score : int) -> int:
        if score and score == self.adv[0]:#PLayerAB always steals when possible
            return score
        return super().play_grill(grill, score)



class Player_select_Tile_equal_score(Player):
    def __init__(self) -> None:
        super().__init__()
        
    def rewardfun(self, score : int, previous_choices : int) -> int:
        if score < self.domino_min or score > self.domino_max or previous_choices % 2 == 0:
            return(-self.C)
        return(self.r[score - self.domino_min])
    
if __name__ == "__main__":
    
    player = Player()
    

    initial_throw = dice2state((1, 1, 2, 4, 4, 4, 5, 0))
    tic = time.time()
    print(player.strategy(initial_throw, 0, 8, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 3, 4, 4, 5, 0))
    tic = time.time()
    print(player.strategy(initial_throw, 0, 8, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 3, 4, 5, 5, 0))
    tic = time.time()
    print(player.strategy(initial_throw, 0, 8, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 3, 5, 5, 5, 0))
    tic = time.time()
    print(player.strategy(initial_throw, 0, 8, 0))
    print(time.time() - tic)
    
    initial_throw = dice2state((1, 3, 3, 5, 5, 5, 5, 0))
    tic = time.time()
    print(player.strategy(initial_throw, 0, 8, 0))
    print(time.time() - tic)
    

    
    throw = dice2state((5,4))
    tic = time.time()
    print(player.strategy(throw, int('11011', 2), 2, 15))
    print(time.time() - tic)
    
    """    
    print(player.expectancy(int('111011', 2), 1, 20))
    
    print(all_possible_dice_outputs(1))
    
    print([proba(dice_output, 1) for dice_output in all_possible_dice_outputs(1)]) 
    
    print([player.strategy(dice_output, int('111011', 2), 1, 20) for dice_output in all_possible_dice_outputs(1)])
                        
    """