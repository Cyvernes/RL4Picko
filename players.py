import functools
import time
import logging
from tools import *



class Player:
    
    def __init__(self) -> None:
        self.N_dice = 8
        self.N_faces = 6
        self.domino_min = 21
        self.domino_max = 36
        self.C = 0
        self.r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        self.dominos = []

    def reinit(self) -> None:
        self.C = 0
        self.r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        self.dominos = []

    def set_C(self, new_C: int):
        logging.debug("cache clear")
        self.expectancy.cache_clear()
        self.strategy.cache_clear()
        self.C = new_C

    def set_r(self, new_r: list[int]):
        logging.debug("cache clear")
        self.expectancy.cache_clear()
        self.strategy.cache_clear()
        self.r = new_r.copy()

    def rewardfun(self, score : int) -> int:
        if score < self.domino_min:
            return(-self.C)
        return(max(self.r[:min(score - self.domino_min , self.domino_max - self.domino_min) + 1]))

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

        :param dice_results: _description_
        :type dice_results: tuple
        :param previous_choices: _description_
        :type previous_choices: int
        :param nb_available_dice: _description_
        :type nb_available_dice: int
        :param score: _description_
        :type score: int
        :return: _description_
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
    
    
    @functools.cache
    def strategy(self, dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int) -> (int, int):
        """Computes the optimal strategy
        
        :param dice_results: Results of the dice. dice_results[i] is the number of dice drawing i. 0 is a worm.
        :type dice_results: tuple
        :param previous_choices: Tells if a choice has already been made
        :type previous_choices: int
        :param nb_available_dice: Number of dice available
        :type nb_available_dice: int
        :param score: current_score
        :type score: int
        """
        # reward init with score if a picko was stashed o/w -C
        reward = self.rewardfun(score) if previous_choices % 2 == 1 else -self.C

        choice = -1
        possible_choices = [i for i in range(len(dice_results)) if dice_results[i] != 0 and ((previous_choices >> i) & 1) == 0]
        for choice_temp in possible_choices:
            new_choices = previous_choices | (1 << choice_temp)
            dice_value = 5 if choice_temp == 0 else choice_temp
            new_score = score + dice_value*dice_results[choice_temp]
            new_nb_available_dice = nb_available_dice - dice_results[choice_temp]
            reward_temp = self.expectancy(new_choices, new_nb_available_dice, new_score)
            if reward_temp > reward:
                reward = reward_temp
                choice = choice_temp
        return(choice, reward)

class PlayerAB(Player):

    def __init__(self) -> None:
        super().__init__()
        self.alpha = 1
        self.beta = 1
        self.adv = (0,0) #(last domino of adversary, reward we get if the player steals it)
    
    def set_ab(self, alpha: int, beta:int) -> None:
        self.alpha = alpha
        self.beta = beta
    
    def rewardfun(self, score : int) -> int:
        if score and score == self.adv[0]:
            return self.adv[1]
        return super().rewardfun(score)

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
        
    def rewardfun(self, score : int) -> int:
        if score < self.domino_min or score > self.domino_max:
            return(-self.C)
        return(self.r[score - self.domino_min])
    
if __name__ == "__main__":
    
    player = Player()
    
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
    
