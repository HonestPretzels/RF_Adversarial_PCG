import os
import gym
import sys
import random
import itertools
import time
from copy import copy
from math import sqrt, log

from vgdl.interfaces.gym import VGDLEnv

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
        start_time = time.time()

        env = VGDLEnv(self.game_path, self.level_path,'image', block_size=10)

        for loop in range(self.loops):

            print('Loop:', loop+1)
            env.render(mode='human')
            env.reset()
            root = Node(None, None)

            best_actions = []
            best_reward = float("-inf")

            for playout in range(self.playouts):
                playout_start = time.time()
                state = copy(env) 

                sum_reward = 0
                node = root
                terminal = False
                actions = []

                # selection
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
                            _, reward, terminal, _ = env.step(action)
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
                print('Playout: %d completed in %f' %(playout+1, time.time() - playout_start))
                

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
            for action in best_actions:
                _, reward, terminal, _ = env.step(action)
                env.render()
                sum_reward += reward
                if terminal:
                    print('terminal')
                    break

            best_rewards.append(sum_reward)
            score = max(moving_average(best_rewards, 100))
            avg_time = (time.time()-start_time)/(loop+1)
            self.record_results(sum_reward, best_actions, time.time()-start_time)
            self.print_stats(loop+1, score, avg_time)


def main():
    # try:
    #     Runner('./games/output/5/cvirsbjuul.txt', './games/output/5/cvirsbjuul_lvl0.txt', './logs/MCTS_cvirsbjuul.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: cvirsbjuul --', e)
    #     with open('./logs/MCTS_cvirsbjuul.txt', 'w') as f:
    #         f.write(str(e))

    # try:
    #     Runner('./games/output/5/cefkjprbjt.txt', './games/output/5/cefkjprbjt_lvl0.txt', './logs/MCTS_cefkjprbjt.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: cefkjprbjt--', e)
    #     with open('./logs/MCTS_cefkjprbjt.txt', 'w') as f:
    #         f.write(str(e))

    # try:
    #     Runner('./games/output/5/kckuxyjwzr.txt', './games/output/5/kckuxyjwzr_lvl0.txt', './logs/MCTS_kckuxyjwzr.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: kckuxyjwzr--', e)
    #     with open('./logs/MCTS_kckuxyjwzr.txt', 'w') as f:
    #         f.write(str(e))
    # try:
    #  Runner('./games/output/5/lgaqxpddxo.txt', './games/output/5/lgaqxpddxo_lvl0.txt', './logs/MCTS_lgaqxpddxo.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: lgaqxpddxo--', e)
    #     with open('./logs/MCTS_lgaqxpddxo.txt', 'w') as f:
    #         f.write(str(e))

    # try:
    #     Runner('./games/output/5/wldxjqwmnk.txt', './games/output/5/wldxjqwmnk_lvl0.txt', './logs/MCTS_wldxjqwmnk.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: wldxjqwmnk--', e)
    #     with open('./logs/MCTS_wldxjqwmnk.txt', 'w') as f:
    #         f.write(str(e))

    # try:
    #     Runner('./games/output/5/ycwjnrcsya.txt', './games/output/5/ycwjnrcsya_lvl0.txt', './logs/MCTS_ycwjnrcsya.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: ycwjnrcsya--', e)
    #     with open('./logs/MCTS_ycwjnrcsya.txt', 'w') as f:
    #         f.write(str(e))
    
    # try:
    #     Runner('./games/output/5/ysbrlmgqbo.txt', './games/output/5/ysbrlmgqbo_lvl0.txt', './logs/MCTS_ysbrlmgqbo.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: ysbrlmgqbo--', e)
    #     with open('./logs/MCTS_ysbrlmgqbo.txt', 'w') as f:
    #         f.write(str(e))
    
    # try:
    #     Runner('./games/output/5/ytiwqqexca.txt', './games/output/5/ytiwqqexca_lvl0.txt', './logs/MCTS_ytiwqqexca.txt', loops=10, playouts=1000, max_depth=50).run()
    # except Exception as e:
    #     print('Error with: ytiwqqexca--', e)
    #     with open('./logs/MCTS_ytiwqqexca.txt', 'w') as f:
    #         f.write(str(e))
    try:
        Runner('./games/training/human/boulderdash.txt', './games/training/human/boulderdash_lvl0.txt', './logs/boulderdash.txt', loops=10, playouts=1000, max_depth=50).run()
    except Exception as e:
        print('Error with: kckuxyjwzr--', e)
        with open('./logs/boulderdash.txt', 'w') as f:
            f.write(str(e))


if __name__ == "__main__":
    main()
