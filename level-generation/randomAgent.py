from vgdl.interfaces.gym import VGDLEnv
from time import time

# prefix = './games/output/5/'
prefix = './games/training/human/'
logPrefix = './logs/'


def logTimeout(game, reward, actionCount):
    logFile = logPrefix + 'RANDOM_' + game + '.txt'
    with open(logFile, 'a') as f:
        f.write('%s TIMED OUT at action %d with score %f\n' %(game, actionCount, reward))

def logCompletion(game, reward, action):
    logFile = logPrefix + 'RANDOM_' + game + '.txt'
    with open(logFile, 'a') as f:
        f.write('%s COMPLETED at action %d with score %f\n' %(game, action, reward))


def runGame(game):
    gameFile = prefix + game + '.txt'
    levelFile = prefix + game + '_lvl0.txt'
    logInterval = 50

    env = VGDLEnv(gameFile, levelFile, 'image', block_size=10)
    startTime = time()
    for loop in range(10):
        score = 0
        env.render(mode='headless')
        env.reset()

        print('Loop: ' + str(loop + 1))
    
        i = 0
        while time() - startTime < 900:
            i += 1
            if i % logInterval == 0:
                print('Action: %d at time %4.2f' %(i, time() - startTime))
            action_id = env.action_space.sample()
            _, reward, isOver, _ = env.step(action_id)
            score += reward
            if isOver:
                logCompletion(game, score, i)
                break
        if time() - startTime > 900:
            logTimeout(game, score, i)
            return

def main():
    # games = ['cefkjprbjt', 'cvirsbjuul', 'kckuxyjwzr', 'lgaqxpddxo', 'wldxjqwmnk', 'ycwjnrcsya', 'ysbrlmgqbo', 'ytiwqqexca']
    games = ['boulderdash']
    for game in games:
        print('Running Game: %s' %game)
        try:
            runGame(game)
        except Exception as e:
            logFile = logPrefix + 'RANDOM_' + game + '.txt'
            with open(logFile, 'a') as f:
                f.write(str(e))

if __name__ == '__main__':
    main()