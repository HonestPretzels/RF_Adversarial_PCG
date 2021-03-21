import os
import sys
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree

from gameComprehension import *
from gameGen import getSpriteByName
from vgdl.parser import Node

sTypes = [
  'RandomNPC',
  'Spreader',
  'OrientedFlicker',
  'Passive',
  'SpawnPoint',
  'Chaser',
  'Resource',
  'Fleeing',
  'Missile',
  'Flicker',
  'Bomber',
  'Immovable',
  'Portal',
  'FlakAvatar',
  'MovingAvatar',
  'ShootAvatar',
]

iTypes = [
  'bounceForward',
  'changeResource',
  'killIfFromAbove',
  'cloneSprite',
  'collectResource',
  'wrapAround',
  'attractGaze',
  'teleportToExit',
  'reverseDirection',
  'stepBack',
  'killIfHasLess',
  'undoAll',
  'turnAround',
  'killIfOtherHasMore',
  'killBoth',
  'pullWithIt',
  'transformTo',
  'killSprite',
]

tTypes = [
  'MultiSpriteCounter',
  'Timeout',
  'SpriteCounter',
  'ResourceCounter',
]

# Returns the paths to all files in the directory given
def getAllFilePaths(dirPath: str):
  return ['%s/%s' % (dirPath, f) for f in os.listdir(dirPath) if os.path.isfile('%s/%s' % (dirPath, f))]

def getAllSpriteCounts(root: Node):
  counts = [0 for _ in sTypes]
  
  def __recurse(node):
    for child in node.children:
      t = child.content.split('>')[1].strip().split(' ')[0].strip()
      if t in sTypes:
        counts[sTypes.index(t)] += 1
      if len(child.children) > 0:
        for grandChild in child.children:
          __recurse(grandChild)

  __recurse(root)
  return counts

def getAllInteractionCounts(root: Node):
  counts = [0 for _ in iTypes]
  
  def __recurse(node):
    for child in node.children:
      t = child.content.split('>')[1].strip().split(' ')[0].strip()
      if t in iTypes:
        counts[iTypes.index(t)] += 1
      if len(child.children) > 0:
        for grandChild in child.children:
          __recurse(grandChild)

  __recurse(root)
  return counts

def getAllTerminationCounts(root: Node):
  counts = [0 for _ in tTypes]
  
  def __recurse(node):
    for child in node.children:
      t = child.content.split(' ')[0].strip()
      if t in tTypes:
        counts[tTypes.index(t)] += 1
      if len(child.children) > 0:
        for grandChild in child.children:
          __recurse(grandChild)

  __recurse(root)
  return counts

def getLevelVector(levelName, mapping, spriteRoot):
  width = 30
  height = 12
  vectorizedLevel = [0]*(width*height) # maximum dimensions of the level

  spriteTypeMapping = {}


  spriteRows = []
  with open(levelName, 'r') as levelFile:
    for line in levelFile.readlines():
      spriteList = []
      for char in line.strip():
        sName = mapping[char].strip().split(' ')[-1]
        sprite = getSpriteByName(spriteRoot, sName)
        spriteType = sprite.content.split('>')[1].strip().split(' ')[0].strip()
        while spriteType not in sTypes:
          spriteType = sprite.parent.content.split('>')[1].strip().split(' ')[0].strip()
          sprite = sprite.parent
        spriteList.append(spriteType)
      spriteRows.append(spriteList)
  for i in range(height):
    if i >= len(spriteRows):
      break
    row = spriteRows[i]
    for j in range(width):
      if j >= len(row):
        continue
      vectorizedLevel[(i*width) + j] = sTypes.index(row[j])
  return vectorizedLevel

def getTerminationData(tRoot, sRoot):
  # Only works for games with 1 win and 1 loss, which should be all
  # Each smaller vector will be [timeoutTime, spritecounterNumber, ResourceCounterNumber]
  winData = [0,0,0,0,0]
  lossData = [0,0,0,0,0]
  for node in tRoot.children:
    if 'win=True' in node.content:
      if 'Timeout' in node.content and 'limit' in node.content:
        winData[0] = int(node.content.split('limit=')[-1].split(' ')[0])
      elif 'SpriteCounter' in node.content and 'limit' in node.content:
        winData[1] = int(node.content.split('limit=')[-1].split(' ')[0])
      elif 'ResourceCounter' in node.content and 'limit' in node.content:
        winData[2] = int(node.content.split('limit=')[-1].split(' ')[0])
      if 'scoreChange' in node.content:
        winData[3] = int(node.content.split('scoreChange=')[-1].split(' ')[0])

      if 'stype' in node.content:
        name = node.content.split('stype=')[-1].split(' ')[0]
        sprite = getSpriteByName(sRoot, name)
        spriteType = sprite.content.split('>')[1].strip().split(' ')[0].strip()
        while spriteType not in sTypes:
          spriteType = sprite.parent.content.split('>')[1].strip().split(' ')[0].strip()
          sprite = sprite.parent
        winData[4] = sTypes.index(spriteType) + 1

    else:
      if 'Timeout' in node.content and 'limit' in node.content:
        lossData[0] = int(node.content.split('limit=')[-1].split(' ')[0])
      elif 'SpriteCounter' in node.content and 'limit' in node.content:
        lossData[1] = int(node.content.split('limit=')[-1].split(' ')[0])
      elif 'ResourceCounter' in node.content and 'limit' in node.content:
        lossData[2] = int(node.content.split('limit=')[-1].split(' ')[0])
      if 'scoreChange' in node.content:
        winData[3] = int(node.content.split('scoreChange=')[-1].split(' ')[0])

      if 'stype' in node.content:
        name = node.content.split('stype=')[-1].split(' ')[0]
        sprite = getSpriteByName(sRoot, name)
        spriteType = sprite.content.split('>')[1].strip().split(' ')[0].strip()
        while spriteType not in sTypes:
          spriteType = sprite.parent.content.split('>')[1].strip().split(' ')[0].strip()
          sprite = sprite.parent
        lossData[4] = sTypes.index(spriteType) + 1

      

  data = []
  data.extend(winData)
  data.extend(lossData)
  return data

def getVector(gameName, levelName):
  # Vector has the form of [total sprite counts, total interaction counts, total termination counts, ...each sprite type count, ...each interaction type count, ...each termination type count]
  # For now only covers sprites with explicit types. As such it makes no differentiation between grass and water in frogger for example.

  spriteRoot = getSpriteSetNode(gameName)
  sCounts = getAllSpriteCounts(spriteRoot)

  interactionRoot = getInteractionSetNode(gameName)
  iCounts = getAllInteractionCounts(interactionRoot)

  terminationRoot = getTerminationSetNode(gameName)
  tCounts = getAllTerminationCounts(terminationRoot)
  tData = getTerminationData(terminationRoot, spriteRoot)

  sTotal = sum(sCounts)
  iTotal = sum(iCounts)
  tTotal = sum(tCounts)

  vector = [sTotal, iTotal, tTotal]
  vector.extend([c for c in sCounts])
  vector.extend([c for c in iCounts])
  vector.extend([c for c in tCounts])
  vector.extend(tData)

  # Add level data
  mapping = extractLevelMapping(gameName)
  level = getLevelVector(levelName, mapping, spriteRoot)
  vector.extend(level)
  return vector

def createClassifier(humanExamples, randomExamples):
  vectors = []
  labels = []
  for game, level in randomExamples.items():
    vectors.append(getVector(game, level))
    labels.append(0)
  for game, level in humanExamples.items():
    vectors.append(getVector(game, level))
    labels.append(1)

  clf = RandomForestClassifier(max_depth=2, random_state=0, n_estimators=100)
  clf.fit(vectors, labels)

  return clf


def main():
  # classification.py path-to-random-training path-to-human-training path-to-test
  # randomGamesPath = sys.argv[1]
  # humanGamesPath = sys.argv[2]

  # allRandoms = getAllFilePaths(randomGamesPath)
  # allHumans = getAllFilePaths(humanGamesPath)

  # correct = 0
  # total = 0

  # clf = createClassifier(allHumans, allRandoms)

  # test = sys.argv[3]

  # p = clf.predict([getVector(test)])
  # print(p)
  
  game = sys.argv[1]
  level = sys.argv[2]

  getVector(game, level)

if __name__ == "__main__":
    main()