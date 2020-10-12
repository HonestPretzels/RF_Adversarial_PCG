import os
import sys
from sklearn.ensemble import RandomForestClassifier

from gameComprehension import *
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


def getVector(fName):
  # Vector has the form of [total sprite counts, total interaction counts, total termination counts, ...each sprite type count, ...each interaction type count, ...each termination type count]
  # For now only covers sprites with explicit types. As such it makes no differentiation between grass and water in frogger for example.

  spriteRoot = getSpriteSetNode(fName)
  sCounts = getAllSpriteCounts(spriteRoot)

  interactionRoot = getInteractionSetNode(fName)
  iCounts = getAllInteractionCounts(interactionRoot)

  terminationRoot = getTerminationSetNode(fName)
  tCounts = getAllTerminationCounts(terminationRoot)

  sTotal = sum(sCounts)
  iTotal = sum(iCounts)
  tTotal = sum(tCounts)

  vector = [sTotal, iTotal, tTotal]
  vector.extend([c for c in sCounts])
  vector.extend([c for c in iCounts])
  vector.extend([c for c in tCounts])

  return vector


def main():
  randomGamesPath = sys.argv[1]
  humanGamesPath = sys.argv[2]

  testPath = sys.argv[3]

  vectors = []
  labels = []
  for f in getAllFilePaths(randomGamesPath):
    vectors.append(getVector(f))
    labels.append(0)
  for f in getAllFilePaths(humanGamesPath):
    vectors.append(getVector(f))
    labels.append(1)

  clf = RandomForestClassifier(max_depth=2, random_state=0)
  clf.fit(vectors, labels)

  p = clf.predict([getVector(testPath)])
  print(p)


if __name__ == "__main__":
    main()