import logging
import os

from tools import *
from players import *

class Game:

    def __init__(self, playerA : Player, playerB : Player) -> None:
        self.domino_min = 21
        self.domino_max = 36
        self.grill = [True for k in range(self.domino_max-self.domino_min+1)]
        self.playerA = playerA
        self.playerB = playerB
        self.N_dice = 8
        self.r = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]

    def reinit(self):
        self.grill = [True for k in range(self.domino_max-self.domino_min+1)]
        self.playerA.reinit()
        self.playerB.reinit()


    def score(self, player):
        if player == 'A':
            return sum((self.r[domino-self.domino_min]  for domino in self.playerA.dominos))
        if player == 'B':
            return sum((self.r[domino-self.domino_min]  for domino in self.playerB.dominos))
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
        
        while 1:
            dice_results = draw_dice(nb_available_dice)
            logging.info(f"dice: {dice_results}")
            player_choice = player.play_dice(dice_results, previous_choices, nb_available_dice, score)
            if player_choice == -1:
                logging.info(f"obtains score: {score}")
                return(score)
            else:
                nb_available_dice -= dice_results[player_choice]
                score += (5 if player_choice == 0 else player_choice)*dice_results[player_choice]
                previous_choices |= 1 << player_choice
            
    
    def play_grill_part(self, player : Player, score : int) -> int:
        logging.info(f"state: {self}")
        player_selection = player.play_grill(self.grill, score)
        return(player_selection)
    
    def play_game(self, display=True):

        playing_player, waiting_player = self.playerA, self.playerB
        
        while not(self.over()):
            if display:
                print(self)
            if playing_player == playerA:
                logging.info("A plays")
            else:
                logging.info("B plays")

            top_domino_waiting_p = waiting_player.dominos[-1] if waiting_player.dominos else 0
            playing_player.init_turn(self.grill,self.r,top_domino_waiting_p)
            player_score = self.play_dice_part(playing_player)
            player_selection = self.play_grill_part(playing_player, player_score)

            if player_selection == player_score:#stealing is possible
                if waiting_player.dominos and player_selection == waiting_player.dominos[-1]:
                    logging.info(f"steals {player_selection}")
                    playing_player.dominos.append(waiting_player.dominos.pop(-1))
                    #new turn
                    playing_player, waiting_player = waiting_player, playing_player
                    continue
            
            if player_selection != -1 and self.grill[player_selection-self.domino_min]:#The playing player has chosen a domino
                logging.info(f"takes {player_selection}")
                self.grill[player_selection-self.domino_min] = False
                playing_player.dominos.append(player_selection) 
               
            else:#The playing player has failed their turn
                lost_domino = None
                if playing_player.dominos:
                    lost_domino = playing_player.dominos.pop(-1)
                    logging.info(f"looses domino {lost_domino}")
                else:
                    logging.info("looses turn")

                for i in range(self.domino_max, self.domino_min-1, -1):
                    if self.grill[i-self.domino_min] and i != lost_domino:
                        game.grill[i-self.domino_min] = False
                        break
            #new turn
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
        
          

    
    

if __name__ == "__main__":

    log_path = 'game.log'
    try:
        os.remove(log_path)
    except OSError:
        pass
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    playerA = Player()
    playerA.set_ab(1,0.1)
    playerB = Player()
    playerB.set_ab(1,0.1)
    game = Game(playerA, playerB)
    score_A, score_B = 0,0
    for _ in range(10):
        game.reinit()
        game.play_game(display=True)
        score_A += game.score("A")
        score_B += game.score("B")
    print(f"Final scores: A = {score_A}, B = {score_B}")

    logging.shutdown()