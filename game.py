from dominos import *
from tools import *
from players import *

class Game:

    def __init__(self, playerA : Player, playerB : Player) -> None:
        self.domino_min = 21
        self.domino_max = 36
        self.grill = [(k>=self.domino_min) for k in range(self.domino_max+1)]
        self.playerA = playerA
        self.playerB = playerB
        self.N_dice = 8
        self.r = [0]*self.domino_min + [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]

    def __str__(self) -> str:
        res = ''.join(["X" if dom else "." for dom in self.grill[self.domino_min:]])
        res += '   ' + str(sum(self.playerA.dominos)).ljust(4) + str(sum(self.playerB.dominos))
        return res

    def over(self) -> bool:
        return(not np.any(self.grill))
    
    def play_dice_part(self, player : Player) -> int:
        nb_available_dice = self.N_dice
        score = 0
        previous_choices = 0
        
        while 1:
            dice_results = draw_dice(nb_available_dice)
            player_choice = player.play_dice(dice_results, previous_choices, nb_available_dice, score)
            if player_choice == -1:
                return(score)
            else:
                nb_available_dice -= dice_results[player_choice]
                score += (5 if player_choice == 0 else player_choice)*dice_results[player_choice]
                previous_choices |= 1 << player_choice
            
    
    def play_grill_part(self, player : Player, score : int) -> int:
        player_selection = player.play_grill(self.grill, score)
        return(player_selection)
    
    def play_a_game(self):
        player_to_play, player_to_wait = self.playerA, self.playerB
        
        while not(self.over()):
            print(self)
            player_score = self.play_dice_part(player_to_play)
            player_selection = self.play_grill_part(player_to_play, player_score)

            if player_selection == player_score:#stealing is possible
                if player_to_wait.dominos and player_selection == player_to_wait.dominos[-1]:
                    self.playerA_dominos.append(self.playerB_dominos.pop(-1))
                    player_to_play, player_to_wait = player_to_wait, player_to_play
                    continue
            
            if self.grill[player_selection] and player_selection != -1:#The playing player has chosen a domino
                self.grill[player_selection] = False
                player_to_play.dominos.append(player_selection) 
               
            else:#The playing player has failed their turn
                lost_domino = None
                if player_to_play.dominos:
                    lost_domino = player_to_play.dominos.pop(-1)

                for i in range(self.domino_max, self.domino_min-1, -1):
                    if self.grill[i] and i != lost_domino:
                        game.grill[i] = False
                        break
            
            player_to_play, player_to_wait = player_to_wait, player_to_play 
        
        final_score_playerA = sum((self.r[domino]  for domino in self.playerA.dominos))
        final_score_playerB = sum((self.r[domino]  for domino in self.playerB.dominos))
        
        rep = "DRAW!"
        if final_score_playerA > final_score_playerB:
            rep = "A wins"
        elif final_score_playerB > final_score_playerA:
            rep = "B wins"
        
        print(rep + "|| PlayerA dominos':", self.playerA.dominos, "| PlayerB dominos':", self.playerB.dominos)
        
          

    
    

if __name__ == "__main__":

    playerA = Player()
    playerB = Player()
    game = Game(playerA, playerB)
    game.play_a_game()

