import functools
import time
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


    def rewardfun(self, score : int) -> int:
        if score < self.domino_min:
            return(self.C)
        else:
            return(max(self.r[:min(score - self.domino_min , self.domino_max - self.domino_min) + 1]))

    def play_dice(self, dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int) -> int:
        """Do the choice when dices are drawn

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
        return(self.strategy(dice_results, previous_choices, nb_available_dice, score)[0])
    
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
        values = [a*b for a,b in zip(grill[self.domino_min :min(score, self.domino_max) + 1], self.r[:score - self.domino_min + 1])]
        domino = np.argmax(values) + self.domino_min
        domino = domino if domino >= self.domino_min else -1
        return(domino)
    
    @functools.cache
    def expectancy(self, choices: int, nb_available_dice: int, score : int) -> float:
        return(sum(
                                proba(dice_output, nb_available_dice) 
                            * self.strategy(dice_output, choices, nb_available_dice, score)[1]
                            for dice_output in all_possible_dice_outputs(nb_available_dice)
                            )
               )
    
    
    @functools.cache
    def strategy(self, dice_results : tuple, previous_choices : int, nb_available_dice : int, score : int):
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
        reward = self.rewardfun(score) if previous_choices % 2 == 1 else self.C
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
    

    
