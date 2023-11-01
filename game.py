from dominos import *

class State:

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

    state = State()

    while not state.over():
        print(state)

        topA = state.A[-1] if state.A else 0
        topB = state.B[-1] if state.B else 0
        dom = ab_strat(state.grill, topA, topB) if state.turnA else ab_strat(state.grill, topB, topA)

        # case where A returns nothing: try putting back last domino earned by A, and remove the best domino
        if dom == 0:
            try:
                lost_dom = state.A.pop() if state.turnA else state.B.pop()
                state.grill[lost_dom] = True
            except IndexError:
                pass
            
            for i in range(DOMINO_MAX,DOMINO_MIN-1, -1):
                if state.grill[i]:
                    state.grill[i] = False
                    break
        
        # steal case
        elif state.turnA and dom == topB:
            state.A.append(state.B.pop())
        elif (not state.turnA) and dom == topA:
            state.B.append(state.A.pop())

        # case where a domino is returned
        elif DOMINO_MIN <= dom <= DOMINO_MAX:
            state.grill[dom] = False
            if state.turnA:
                state.A.append(dom)
            else:
                state.B.append(dom)
        
        # error case
        else:
            raise IndexError
        
        state.turnA = not state.turnA