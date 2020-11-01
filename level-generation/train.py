import os
import sys
import random

from gameGen import subGen
from classification import createClassifier, getVector, getAllFilePaths

def main():
    humanGames = getAllFilePaths(sys.argv[1])
    randomGames = getAllFilePaths(sys.argv[2])

    clf = createClassifier(humanGames, randomGames)

    validationGames = getAllFilePaths(sys.argv[3])
    predictedAsHuman = []
    human_threshold = 0.9
    neighbourCount = 8

    iterations = 1
    while len(predictedAsHuman) == 0 and iterations < 200:
        
        neighboursDict = {}
        for game in validationGames:
            prob_human = clf.predict_proba([getVector(game)])[0][1]
            if prob_human > human_threshold:
                predictedAsHuman.append(game)
                break
            neighbours = genNeighbours(game, neighbourCount)
            neighboursDict[game] = neighbours

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
    for game in neighboursDict.keys():
        currMax = clf.predict_proba([getVector(game)])[0][1]
        currBest = game
        for neighbour in neighboursDict[game]:
            prob = clf.predict_proba([getVector(neighbour)])[0][1]
            if prob >= currMax:
                currBest = neighbour
                currMax = prob
        probs.append(currMax)
        if currBest == game:    # Encourage exploration if stuck
            currBest = random.choice(neighboursDict[game])
        
        replaceFile(game, currBest)
    return sum(probs)/len(probs), max(probs)

def replaceFile(original, new):
    with open(original, 'w') as original:
        with open(new, 'r') as new:
            original.write(new.read())

def genNeighbours(gamePath, n):
    neighbours = []
    neighbourFolder = '.' + gamePath.split('.')[1] + '_neighbours'
    if not os.path.isdir(neighbourFolder):
        os.mkdir(neighbourFolder)
    for i in range(n):
        gameName = gamePath.split('/')[-1].split('.')[0]
        choice = random.randint(0,2)
        output = neighbourFolder + '/' + str(i)  + '.txt'
        subGen(gamePath, output, int(choice == 0), int(choice == 1), int(choice == 2))
        neighbours.append(output)
    return neighbours


if __name__ == "__main__":
    main()