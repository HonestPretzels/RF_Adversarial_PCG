import os
import sys
import random

from gameGen import subGen
from classification import createClassifier, getVector, getAllFilePaths

def main():
    humanGameFiles = getAllFilePaths(sys.argv[1])
    humanGames = {}
    for game in humanGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            humanGames[gameName] = game
    randomGameFiles = getAllFilePaths(sys.argv[2])
    randomGames = {}
    for game in randomGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            randomGames[gameName] = game
    iterationGameFiles = getAllFilePaths(sys.argv[3])
    iterationGames = {}
    for game in iterationGameFiles:
        if '_lvl' in game:
            gameName = game.split('_')[0] + '.txt'
            iterationGames[gameName] = game

    clf = createClassifier(humanGames, randomGames)

    predictedAsHuman = []
    human_threshold = 0.9
    neighbourCount = 8
    iterations = 1
    
    while len(predictedAsHuman) == 0 and iterations < 200:
        neighboursDict = {}
        for game, level in iterationGames.items():
            prob_human = clf.predict_proba([getVector(game, level)])[0][1]
            if prob_human > human_threshold:
                predictedAsHuman.append((game, level))
                break
            neighbours = genNeighbours(game, level, neighbourCount)
            neighboursDict[(game, level)] = neighbours

        avg_prob, best = replaceWithBestNeighbours(neighboursDict, clf)
        print('training iteration: %d with average score: %.3f and best score %.3f' %(iterations, avg_prob, best))
        iterations += 1

    if len(predictedAsHuman) < 1:
        b = None
        p = 0
        for game in validationGames:
            prob = clf.predict_proba([getVector(game)])[0][1]
            if prob > p:
                b = game
                p = prob
        predictedAsHuman.append(b)
    print(predictedAsHuman, iterations)
    
    

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

def genNeighbours(gamePath, levelPath, n):
    neighbours = []
    neighbourFolder = '.' + gamePath.split('.')[1] + '_neighbours'
    if not os.path.isdir(neighbourFolder):
        os.mkdir(neighbourFolder)
    for i in range(n):
        gameName = gamePath.split('/')[-1].split('.')[0]
        choice = random.randint(0,2)
        output = neighbourFolder + '/' + str(i)  + '.txt'
        levelOutPut = neighbourFolder + '/' + str(i)  + '_lvl0.txt'
        subGen(gamePath, output, int(choice == 0), int(choice == 1), int(choice == 2), levelPath, levelOutPut)
        neighbours.append((output, levelOutPut))
    return neighbours


if __name__ == "__main__":
    main()