import os
import sys
import random
import shutil

from gameGen import subGen, generateRandomGames
from levelGen import makeSubstitution, addRow, deleteRow, addColumn, deleteColumn
from classification import createClassifier, getVector, getAllFilePaths

###### RUN AS FOLLOWS
###### python .\train.py [path to human training data folder] [path to random training folder] [path to use for temp iterations]
###### Note everything in random and iteration folder will be deleted and replaced
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
    shutil.rmtree(randomGamePath)
    os.mkdir(randomGamePath)
    generateRandomGames(randomGamePath, 8)
    
    randomGameFiles = getAllFilePaths(randomGamePath)
    randomGames = {}
    for game in randomGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            randomGames[gameName] = game

    # generate games to iterate through
    iterationGamePath = sys.argv[3]
    shutil.rmtree(iterationGamePath)
    os.mkdir(iterationGamePath)
    generateRandomGames(iterationGamePath, 8)

    iterationGameFiles = getAllFilePaths(iterationGamePath)
    iterationGames = {}
    for game in iterationGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            iterationGames[gameName] = game

    clf = createClassifier(humanGames, randomGames)

    predictedAsHuman = set([])
    human_threshold = 0.95
    neighbourCount = 8
    levelNeighbourCount = 8
    iterations = 1

    while iterations < 200:
        neighboursDict = {}
        stopFlag = False
        prob_human_avg = 0
        for game, level in iterationGames.items():
            prob_human_game = clf.predict_proba([getVector(game, level)])[0][1]
            if prob_human_game > human_threshold:
                predictedAsHuman.add((game, level))
            prob_human_avg += prob_human_game / len(iterationGames)
            neighbours = genNeighbours(game, level, neighbourCount, levelNeighbourCount)
            neighboursDict[(game, level)] = neighbours


        # Average probability across all games > threshold
        if prob_human_avg > human_threshold:
            print('training complete at iteration: %d with score: %.3f' %(iterations, prob_human_avg))
            break
        else:
            avg_prob, best = replaceWithBestNeighbours(neighboursDict, clf)
            print('training iteration: %d with average score: %.3f and best score %.3f' %(iterations, avg_prob, best))
            iterations += 1

    if len(predictedAsHuman) < 1:
        b = None
        p = 0
        for game, level in iterationGames.items():
            prob = clf.predict_proba([getVector(game, level)])[0][1]
            if prob > p:
                b = (game, level)
                p = prob
        predictedAsHuman.append(b)
    print(predictedAsHuman)
    
    

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
    return sum(probs)/len(probs), max(probs)

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