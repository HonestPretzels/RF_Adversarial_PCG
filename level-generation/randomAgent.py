import sys
import os

from vgdl.interfaces.gym import VGDLEnv
from classification import getAllFilePaths

from time import time

# prefix = './games/output/5/'
prefix = './games/training/human/'
logPrefix = './logs/'


def logTimeout(game, logs, reward, actionCount):
    logs
    with open(logs, 'a') as f:
        f.write('%s TIMED OUT at action %d with score %f\n' %(game, actionCount, reward))

def logCompletion(game, logs, reward, action):
    with open(logs, 'a') as f:
        f.write('%s COMPLETED at action %d with score %f\n' %(game, action, reward))


def runGame(gameFile, levelFile, logs):
    logInterval = 50

    env = VGDLEnv(gameFile, levelFile, 'image', block_size=10)
    startTime = time()
    for loop in range(10):
        score = 0
        env.render(mode='headless')
        env.reset()

        print('Loop: ' + str(loop + 1))
    
        i = 0
        while time() - startTime < 300 and i < 500:
            i += 1
            if i % logInterval == 0:
                print('Action: %d at time %4.2f' %(i, time() - startTime))
            action_id = env.action_space.sample()
            env.render(mode='headless')
            _, reward, isOver, _ = env.step(action_id)
            score += reward
            if isOver:
                logCompletion(os.path.basename(gameFile), logs, score, i)
                break
        if time() - startTime > 300 or i >= 500:
            logTimeout(os.path.basename(gameFile), logs, score, i)
            return

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
        logs = os.path.join(logDirectory, 'RANDOM_' + os.path.basename(game))
        try:
            runGame(game, level, logs)
        except Exception as e:
            with open(logs, 'a') as f:
                f.write(str(e))

        

if __name__ == '__main__':
    main()