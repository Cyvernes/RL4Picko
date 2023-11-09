import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from game import *

HID_SIZE = 10
STATE_SIZE = 16*3

GAMMA = 1
LR = 0.001
LOSS_AB = 10
N_SIMU = 3

def state2tensor(grill, me, adv):
    return torch.tensor(grill + me + [0]*(16-len(me)) + adv  + [0]*(16-len(adv)), dtype=torch.float32)

def tensor2state(vec):
    res = vec.tolist()
    grill = res[0:16]
    me = res[16:32]
    adv = res[32:48]
    return grill, [x for x in me if x], [x for x in adv if x]

class Actor(nn.Module):
    def __init__(self):
        super(Actor, self).__init__()

        self.base = nn.Sequential(
            nn.Linear(STATE_SIZE, HID_SIZE),
            nn.ReLU(),
        )
        self.alpha = nn.Sequential(
            nn.Linear(HID_SIZE, 1),
            nn.Softplus(),
        )
        self.beta = nn.Sequential(
            nn.Linear(HID_SIZE, 1),
            nn.Softplus(),
        )
        self.value = nn.Sequential(
            nn.Linear(HID_SIZE, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        base_out = self.base(x)
        return self.alpha(base_out), self.beta(base_out), self.value(base_out)

class Agent():
    def __init__(self, net) -> None:
        self.net = net
        self.me = PlayerAB()
        self.adv = PlayerAB()
        self.game = Game(self.me, self.adv)

    def simulator(self, alpha, beta) -> torch.Tensor:
        save_grill = self.game.grill.copy()
        save_me = self.me.dominos.copy()
        save_adv = self.adv.dominos.copy()
        self.me.set_ab(alpha, beta)

        res = 0

        for _ in range(N_SIMU):
            reward = self.game.play_turn(self.me, self.adv)
            reward -= self.game.play_turn(self.adv, self.me)
            new_state = state2tensor(self.game.grill, self.me.dominos, self.adv.dominos)

            with torch.no_grad():
                _, _, new_val = self.net(new_state)
            res += reward + GAMMA*new_val[0]

            self.game.grill = save_grill.copy()
            self.me.dominos = save_me.copy()
            self.adv.dominos = save_adv.copy()

        return res / N_SIMU

if __name__ == "__main__":

    #Logging
    log_path = 'game.log'
    try:
        os.remove(log_path)
    except OSError:
        pass
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Initialize the network and optimizer
    net = Actor()
    agent = Agent(net)

    optimizer = optim.SGD(agent.net.parameters(), lr=LR)

    # Training loop
    for epoch in range(10):
        
        agent.game.reinit()

        while not agent.game.over():

            state = state2tensor(agent.game.grill, agent.me.dominos, agent.adv.dominos)
            alpha, beta, val = agent.net(state)
            agent.me.set_ab(alpha.item(), beta.item())

            reward = agent.game.play_turn(agent.me, agent.adv)
            if not agent.game.over():
                reward -= agent.game.play_turn(agent.adv, agent.me)
            print(f"step done {alpha.item():.2f} - {beta.item():.2f} : {val.item():.2f} with reward {reward}")

            # Simulate
            max_val = None
            best_alpha = None
            best_beta = None
            for a in np.logspace(-2, 1, 10):
                for b in np.logspace(-2, 1, 10):
                    v = agent.simulator(a, b)
                    if max_val == None or v > max_val:
                        max_val = v
                        best_alpha = a
                        best_beta = b
            print(f"simu done {best_alpha:.2f} - {best_beta:.2f} : {max_val:.2f}")

            # Loss
            optimizer.zero_grad()
            loss = (reward + GAMMA*max_val - val) + LOSS_AB*((best_alpha-alpha)**2 + (best_beta-beta)**2)
            loss.backward()
            optimizer.step()
            print(f"optimization done: loss = {loss.item()}")

        print(f"Epoch {epoch+1}, Loss: {loss.item()}")
