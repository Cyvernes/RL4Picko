from dominos import *

class Game:

    def __init__(self) -> None:
        self.grill = [(k>=DOMINO_MIN) for k in range(DOMINO_MAX+1)]
        self.A = []
        self.B = []
        self.turnA = True

    def __str__(self) -> str:
        res = ''.join(["X" if dom else "." for dom in self.grill[DOMINO_MIN:]])
        res += '   ' + str(sum(self.A)).ljust(4) + str(sum(self.B))
        return res

    def over(self) -> bool:
        for el in self.grill[DOMINO_MIN:]:
            if el:
                return False
        return True

if __name__ == "__main__":

    game = Game()

    while not game.over():
        print(game)

        topA = game.A[-1] if game.A else 0
        topB = game.B[-1] if game.B else 0
        dom = ab_strat(game.grill, topA, topB) if game.turnA else ab_strat(game.grill, topB, topA)

        # case where A returns nothing: try putting back last domino earned by A, and remove the best domino
        if dom == 0:
            try:
                lost_dom = game.A.pop() if game.turnA else game.B.pop()
                game.grill[lost_dom] = True
            except IndexError:
                pass
            
            for i in range(DOMINO_MAX,DOMINO_MIN-1, -1):
                if game.grill[i]:
                    game.grill[i] = False
                    break
        
        # steal case
        elif game.turnA and dom == topB:
            game.A.append(game.B.pop())
        elif (not game.turnA) and dom == topA:
            game.B.append(game.A.pop())

        # case where a domino is returned
        elif DOMINO_MIN <= dom <= DOMINO_MAX:
            game.grill[dom] = False
            if game.turnA:
                game.A.append(dom)
            else:
                game.B.append(dom)
        
        # error case
        else:
            raise IndexError
        
        game.turnA = not game.turnA