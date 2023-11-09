import logging
import os

from tools import *
from players import *

class Game:

    def __init__(self, playerA : Player, playerB : Player, N_dice = 8, domino_min = 21, domino_max = 36, r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]) -> None:
        self.domino_min = domino_min
        self.domino_max = domino_max
        self.grill = (self.domino_max-self.domino_min+1)
        self.playerA = playerA
        self.playerB = playerB
        self.N_dice = N_dice
        self.r = r

    def reinit(self):
        self.grill = [True]* (self.domino_max-self.domino_min+1)
        self.playerA.reinit()
        self.playerB.reinit()


    def score(self, player):
        if player == 'A':
            return sum((self.r[domino-self.domino_min] for domino in self.playerA.dominos))
        if player == 'B':
            return sum((self.r[domino-self.domino_min] for domino in self.playerB.dominos))
        return ValueError

    def __str__(self) -> str:
        res = ''.join(["X" if dom else "." for dom in self.grill])
        res += '   ' + str(self.playerA.dominos[-1] if self.playerA.dominos else 0).ljust(4)
        res += str(self.playerB.dominos[-1] if self.playerB.dominos else 0).ljust(4)
        return res

    def over(self) -> bool:
        return(not np.any(self.grill))
    
            
    def play_dice_part(self, player : Player) -> int:
        nb_available_dice = self.N_dice
        score = 0
        previous_choices = 0
        for i in range(8): # At each turn, the number of dice is decreased by at least one (or the round is stopped). Thus we do at most 8 turns.
            # Draw the dice
            dice_results = draw_dice(nb_available_dice)
            logging.info(f"dice: {dice_results}")
            # Send the result to the play and let them chose what to do
            player_choice = player.play_dice(dice_results, previous_choices, nb_available_dice, score)
            logging.info(f" player's choice: {player_choice}")
            
            if player_choice is None:# The Player can't choose, the round is failed
                logging.info(f" player fails, reward = {-player.C}")
                return(-player.C)
            else:
                score += (player_choice[0] if player_choice[0] else 5)*dice_results[player_choice[0]]
                previous_choices |= 1 << player_choice[0]
                if player_choice[1]:# Player decides to continue
                    nb_available_dice -= dice_results[player_choice[0]]
                    continue
                else:# player decides to stop
                    logging.info(f" player stops, reward = {score}")
                    return(score)
    
    
    def play_grill_part(self, player : Player, score : int) -> int:
        logging.info(f"state: {self}")
        player_selection = player.play_grill(self.grill, score)
        return(player_selection)
    
    def play_turn(self, playing_player: Player, waiting_player:Player) -> int:
        playing_player.init_turn(self.grill,self.r,waiting_player.dominos)
        player_score = self.play_dice_part(playing_player)
        player_selection = self.play_grill_part(playing_player, player_score)

        if player_selection == player_score:#stealing is possible
            if waiting_player.dominos and player_selection == waiting_player.dominos[-1]:
                logging.info(f"steals {player_selection}")
                playing_player.dominos.append(waiting_player.dominos.pop(-1))
                #new turn
                playing_player, waiting_player = waiting_player, playing_player
                return 2*self.r[player_selection-self.domino_min]
        
        if player_selection != -1 and self.grill[player_selection-self.domino_min]:#The playing player has chosen a domino
            logging.info(f"takes {player_selection}")
            self.grill[player_selection-self.domino_min] = False
            playing_player.dominos.append(player_selection) 
            return self.r[player_selection-self.domino_min]
            
        else:#The playing player has failed their turn
            lost_domino = None
            res = 0
            if playing_player.dominos:
                lost_domino = playing_player.dominos.pop(-1)
                logging.info(f"looses domino {lost_domino}")
                res = -self.r[lost_domino-self.domino_min]
            else:
                logging.info("looses turn")

            for i in range(self.domino_max, self.domino_min-1, -1):
                if self.grill[i-self.domino_min] and i != lost_domino:
                    self.grill[i-self.domino_min] = False
                    return res
            return res

    def play_game(self, display=True):
        """_summary_

        :param display: _description_, defaults to True
        :type display: bool, optional
        """

        playing_player, waiting_player = self.playerA, self.playerB
        
        while not(self.over()):
            if display:
                print(self)
            if playing_player == self.playerA:
                logging.info("A plays")
            else:
                logging.info("B plays")
            
            self.play_turn(playing_player, waiting_player)
            playing_player, waiting_player = waiting_player, playing_player 

        if display:
            final_score_playerA = self.score("A")
            final_score_playerB = self.score("B")

            rep = "DRAW!"
            if final_score_playerA > final_score_playerB:
                rep = "A wins"
            elif final_score_playerB > final_score_playerA:
                rep = "B wins"
            
            print(rep + "|| PlayerA dominos':", self.playerA.dominos, "| PlayerB dominos':", self.playerB.dominos)
        

class GD:

    def __init__(self, n_epochs, n_batchs, h = 0.01, lr = 0.1) -> None:
        self.n_epochs = n_epochs
        self.n_batchs = n_batchs
        self.h = h
        self.lr = lr
        
        self.epoch = 1
        self.alpha = 1
        self.beta = 1

        self.alphas = [1]
        self.betas = [1]

        self.playerA = PlayerAB()
        self.playerB = PlayerAB()
        self.playerB.set_ab(1,1)
        self.game = Game(self.playerA, self.playerB)
    
    def simu(self, a, b) -> float:
        self.playerA.set_ab(a, b)
        res = 0
        for batch in range(self.n_batchs):
            self.game.reinit()
            self.game.play_game(display=False)
            res -= self.game.score("A") - self.game.score("B") # descent so negative
        return res/self.n_batchs

    def gradient_descent(self):
        for epoch in range(self.n_epochs):

            fab = self.simu(self.alpha, self.beta)
            fahb = self.simu(self.alpha + self.h, self.beta)
            fabh = self.simu(self.alpha, self.beta + self.h)

            self.alpha -= (fahb - fab) * (self.lr/self.epoch)
            self.beta -= (fabh - fab) * (self.lr/self.epoch)

            self.alphas.append(self.alpha)
            self.betas.append(self.betas)

if __name__ == "__main__":

    log_path = 'game.log'
    try:
        os.remove(log_path)
    except OSError:
        pass
    logging.basicConfig(filename=log_path, level=logging.NOTSET, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    gd = GD(10, 3)
    gd.gradient_descent()

    logging.shutdown()