import os
import sys
import random
import shutil
from time import time
from vgdl.interfaces.gym import VGDLEnv

from gameGen import subGen, generateRandomGames
from levelGen import makeSubstitution, addRow, deleteRow, addColumn, deleteColumn
from classification import createClassifier, getVector, getAllFilePaths

###### RUN AS FOLLOWS
###### python .\classifierGenerate.py [path to human training data folder] [path to random training folder] [path to use for temp iterations] [path for output folder] -New?
###### Note everything in random will be replaced if -New is used
###### Then run this:
###### python -m vgdl.util.humanplay.play_vgdl [path to level file] -d [path to game description file]
###### IF INSTALLING PY-VGDL FAILS
###### delete the folder py-vgdl, reclone it from here https://github.com/rubenvereecken/py-vgdl, and run pip install -e 'py-vgdl[all]'


def main():
    humanGameFiles = getAllFilePaths(sys.argv[1])
    humanGames = {}
    for game in humanGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            humanGames[gameName] = game

    # generate random games
    randomGamePath = sys.argv[2]
    
    outputPath = sys.argv[4]


    # To generate new random games for classifier instead of using current ones
    if len(sys.argv) == 6 and sys.argv[5] == '-New':
        shutil.rmtree(randomGamePath)
        os.mkdir(randomGamePath)
        generateRandomGames(randomGamePath, 8)
    
    randomGameFiles = getAllFilePaths(randomGamePath)
    randomGames = {}
    for game in randomGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            randomGames[gameName] = game

    # generate a game to iterate on
    iterationGamePath = sys.argv[3]
    clf = createClassifier(humanGames, randomGames)
    finishedGames = 0
    failedGameCount = 0
    while finishedGames < 8:
        print('Generating game: %d'%(finishedGames + 1))
        finishedGame, finishedLevel = generateOneGame(iterationGamePath, clf)
        if not finishedGame:
            failedGameCount += 1
            continue
        else:
            finishedGames += 1
            outG = os.path.join(outputPath, os.path.basename(finishedGame))
            outL = os.path.join(outputPath, os.path.basename(finishedLevel))
            copyFile(finishedGame, outG)
            copyFile(finishedLevel, outL)
    
    print('Game generation complete. %d failures occured'%failedGameCount)

def generateOneGame(iterationGamePath, clf):
    shutil.rmtree(iterationGamePath)
    os.mkdir(iterationGamePath)
    generateRandomGames(iterationGamePath, 1)

    iterationGameFiles = getAllFilePaths(iterationGamePath)
    iterationGames = {}
    for game in iterationGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            iterationGames[gameName] = game


    human_threshold = 0.95
    neighbourCount = 8
    levelNeighbourCount = 8
    iterations = 0

    while iterations < 200:
        neighboursDict = {}
        for game, level in iterationGames.items():
            prob_human_game = clf.predict_proba([getVector(game, level)])[0][1]
            neighbours = genNeighbours(game, level, neighbourCount, levelNeighbourCount)
            neighboursDict[(game, level)] = neighbours
        if prob_human_game > human_threshold:
            break


        
        best = replaceWithBestNeighbours(neighboursDict, clf)
        print('generate iteration: %d with score: %.3f' %(iterations + 1, best))
        iterations += 1
    
    if iterations >= 200:
        print('Game generation did not hit the threshold')
        return None, None
    
    if ensurePlayable(game, level):
        return (game, level)
    else:
        return None, None

    
def ensurePlayable(game, level):
    print('Testing Playability...')
    try:
        env = VGDLEnv(game, level, 'image', block_size=10)
        env.render(mode="headless")
        env.reset()
    except:
        return False

    thresholdDifference = 1

    for _ in range(400):
        start = time()
        try:
            env.step(env.action_space.sample())
        except:
            print('Errored Out')
            return False
        
        end = time()
        if end - start > thresholdDifference:
            print('Timed Out')
            return False
    return True


def replaceWithBestNeighbours(neighboursDict, clf):
    probs = []
    for game, level in neighboursDict.keys():
        currMax = clf.predict_proba([getVector(game, level)])[0][1]
        currBest = (game, level)
        for neighbour, neighbourLevel in neighboursDict[(game, level)]:
            prob = clf.predict_proba([getVector(neighbour, neighbourLevel)])[0][1]
            if prob >= currMax:
                currBest = (neighbour, neighbourLevel)
                currMax = prob
        probs.append(currMax)
        if currBest == game:    # Encourage exploration if stuck
            currBest = random.choice(neighboursDict[(game, level)])
        
        replaceFile(game, currBest[0])
        replaceFile(level, currBest[1])
    return max(probs)

def replaceFile(original, new):
    with open(original, 'w') as original:
        with open(new, 'r') as new:
            original.write(new.read())

def copyFile(original, new):
    with open(original, 'r') as original:
        with open(new, 'w') as new:
            new.write(original.read())

def genNeighbours(gamePath, levelPath, n, l):
    neighbours = []
    neighbourFolder = '.' + gamePath.split('.')[1] + '_neighbours'
    if not os.path.isdir(neighbourFolder):
        os.mkdir(neighbourFolder)
    
    # Rule changes
    for i in range(n):
        choice = random.randint(0,2)
        output = neighbourFolder + '/' + str(i)  + '.txt'
        levelOutPut = neighbourFolder + '/' + str(i)  + '_lvl0.txt'
        subGen(gamePath, output, int(choice == 0), int(choice == 1), int(choice == 2), levelPath, levelOutPut)
        neighbours.append((output, levelOutPut))

    # Level Substitutions
    for j in range(n, n + l):
        output = neighbourFolder + '/' + str(j) + '.txt'
        levelOutput = neighbourFolder + '/' + str(j) + '_lvl0.txt'
        copyFile(gamePath, output)
        makeSubstitution(gamePath, levelPath, levelOutput, 10)
        neighbours.append((output, levelOutput))

    # Row Delete
    output = neighbourFolder + '/' + str(n+l+1) + '.txt'
    levelOutput = neighbourFolder + '/' + str(n+l+1) + '_lvl0.txt'
    changeHappened = deleteRow(levelPath, levelOutput)
    if changeHappened:
        copyFile(gamePath, output) 
        neighbours.append((output, levelOutput))

    # Row Add
    output = neighbourFolder + '/' + str(n+l+2) + '.txt'
    levelOutput = neighbourFolder + '/' + str(n+l+2) + '_lvl0.txt'
    changeHappened = addRow(levelPath, levelOutput, gamePath)
    if changeHappened:
        copyFile(gamePath, output) 
        neighbours.append((output, levelOutput))

    # Column Delete
    output = neighbourFolder + '/' + str(n+l+3) + '.txt'
    levelOutput = neighbourFolder + '/' + str(n+l+3) + '_lvl0.txt'
    changeHappened = deleteColumn(levelPath, levelOutput)
    if changeHappened:
        copyFile(gamePath, output) 
        neighbours.append((output, levelOutput))

    # Column Add
    output = neighbourFolder + '/' + str(n+l+4) + '.txt'
    levelOutput = neighbourFolder + '/' + str(n+l+4) + '_lvl0.txt'
    changeHappened = addColumn(levelPath, levelOutput, gamePath)
    if changeHappened:
        copyFile(gamePath, output) 
        neighbours.append((output, levelOutput))
        

    return neighbours


if __name__ == "__main__":
    main()