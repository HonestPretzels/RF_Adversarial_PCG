import os
import gym
import sys
import random
import itertools
import time
from copy import copy
from math import sqrt, log

from vgdl.interfaces.gym import VGDLEnv
from classification import getAllFilePaths

#https://gist.github.com/blole/dfebbec182e6b72ec16b66cc7e331110   FROM HERE

def moving_average(v, n):
    n = min(len(v), n)
    ret = [.0]*(len(v)-n+1)
    ret[0] = float(sum(v[:n]))/n
    for i in range(len(v)-n):
        ret[i+1] = ret[i] + float(v[n+i] - v[i])/n
    return ret


def ucb(node):
    return node.value / node.visits + sqrt(log(node.parent.visits)/node.visits)


def combinations(space):
    if isinstance(space, gym.spaces.Discrete):
        return range(space.n)
    elif isinstance(space, gym.spaces.Tuple):
        return itertools.product(*[combinations(s) for s in space.spaces])
    else:
        raise NotImplementedError


class Node:
    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        self.children = []
        self.explored_children = 0
        self.visits = 0
        self.value = 0


class Runner:
    def __init__(self, game_path, level_path, out_path, loops=300, max_depth=1000, playouts=10000):
        self.game_path = game_path
        self.level_path = level_path
        self.loops = loops
        self.max_depth = max_depth
        self.playouts = playouts
        self.out_path = out_path
        self.max_time = 300

    def print_stats(self, loop, score, avg_time):
        print('\r%3d   score:%10.3f   avg_time:%4.1f s' % (loop, score, avg_time))
    
    def record_results(self, reward, actions, time):
        out = 'MCTS COMPLETED %s WITH REWARD %d AND LENGTH %d AND TIME %4.1f\n' % (self.game_path.split('/')[-1], reward, len(actions), time)
        print(out)
        with open(self.out_path, 'a') as f:
            f.write(out)
    
    def record_timeout(self, time, reward, actions):
        out = 'MCTS TIMED OUT %s WITH TIME %4.1f, REWARD IS %f AT ACTION %d\n' % (self.game_path.split('/')[-1], time, reward, len(actions))
        print(out)
        with open(self.out_path, 'a') as f:
            f.write(out)

    def run(self):
        best_rewards = []

        env = VGDLEnv(self.game_path, self.level_path,'objects', block_size=10)

        for loop in range(self.loops):
            start_time = time.time()
            print('Loop:', loop+1)
            env.render(mode='headless')
            env.reset()
            root = Node(None, None)

            best_actions = []
            best_reward = float("-inf")

            for playout in range(self.playouts):
                # RESET TO EQUAL COPYING AN EMPTY STATE --- THINK THIS THROUGH AGAIN LATER
                env.render(mode='headless')
                env.reset()
                state = copy(env) 

                sum_reward = 0
                node = root
                terminal = False
                actions = []

                # selection
                # This also catches us up to the state, assuming that the env is deterministic
                while node.children:
                    if node.explored_children < len(node.children):
                        child = node.children[node.explored_children]
                        node.explored_children += 1
                        node = child
                    else:
                        node = max(node.children, key=ucb)
                    _, reward, terminal, _ = state.step(node.action)
                    sum_reward += reward
                    actions.append(node.action)

                # expansion
                if not terminal:
                    node.children = [Node(node, a) for a in combinations(state.action_space)]
                    random.shuffle(node.children)

                # playout
                while not terminal:
                    if time.time() - start_time > 300:
                        sum_reward = 0
                        for action in best_actions:
                            state.render(mode="headless")
                            _, reward, terminal, _ = state.step(action)
                            sum_reward += reward
                            if terminal:
                                break
                        self.record_timeout(time.time() - start_time, sum_reward, best_actions)
                        best_rewards.append(sum_reward)
                        score = max(moving_average(best_rewards, 100))
                        avg_time = (time.time()-start_time)/(loop+1)
                        self.print_stats(loop+1, score, avg_time)
                        return

                    action = state.action_space.sample()
                    _, reward, terminal, _ = state.step(action)

                    sum_reward += reward
                    actions.append(action)

                    if len(actions) > self.max_depth:
                        sum_reward -= 100
                        break
                # print('Playout: %d completed in %f' %(playout+1, time.time() - playout_start))
                

                # remember best
                if best_reward < sum_reward:
                    best_reward = sum_reward
                    best_actions = actions

                # backpropagate
                while node:
                    node.visits += 1
                    node.value += sum_reward
                    node = node.parent

            sum_reward = 0
            print(best_actions)
            env.render(mode="headless")
            env.reset()
            # Go through best actions
            terminated = False
            for action in best_actions:
                env.render(mode="headless")
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward
                if terminal:
                    terminated = True
                    break
            
            # Take random actions until terminal or another 300 moves occured
            actionCounter = 0
            while not terminated and actionCounter < 300:
                env.render(mode="headless")
                action = env.action_space.sample()
                best_actions.append(action)
                _, reward, terminal, _ = env.step(action)
                sum_reward += reward
                actionCounter += 1
                if terminal:
                    terminated = True
                    break

            best_rewards.append(sum_reward)
            score = max(moving_average(best_rewards, 100))
            avg_time = (time.time()-start_time)
            if terminated:
                self.record_results(sum_reward, best_actions, time.time()-start_time)
            else:
                self.record_timeout(time.time()-start_time, sum_reward, best_actions)
            self.print_stats(loop+1, score, avg_time)


def main():
    gameDirectory = sys.argv[1]
    logDirectory = sys.argv[2]
    gamePaths = getAllFilePaths(gameDirectory)
    games = {}
    for game in gamePaths:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            games[gameName] = game
    for game, level in games.items():
        logs = os.path.join(logDirectory, 'MCTS_' + os.path.basename(game))
        try:
            Runner(game, level, logs, loops=5, playouts=500, max_depth=200).run()
        except Exception as e:
            print('Error with: %s -- %s' %(os.path.basename(game), e))
            with open(logs, 'w') as f:
                f.write(str(e))

if __name__ == "__main__":
    main()
