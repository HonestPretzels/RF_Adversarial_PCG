import sys, os, csv

if __name__ == '__main__':
    inputPath = sys.argv[1]
    output = sys.argv[2]

    with open(output, 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerow(['Game', 'Experiment', 'Iteration', 'Mode', 'Completed', 'Score', 'Moves'])

        experiments = [f.path for f in os.scandir(inputPath) if f.is_dir()]
        for experiment in experiments:
            iterations = [f.path for f in os.scandir(experiment) if f.is_dir()]
            for iteration in iterations:
                games = [f.path for f in os.scandir(iteration) if f.is_file()]
                for game in games:
                    game_name = os.path.basename(game).split('.')[0].split('_')[1]
                    exp = os.path.basename(experiment)
                    it = os.path.basename(iteration)
                    mode = os.path.basename(game).split('.')[0].split('_')[0]
                    with open(game, 'r') as gf:
                        line = gf.readline()
                        splitLine = line.split(' ')

                        if 'COMPLETED' in line:
                            completed = '1'
                        else:
                            completed = '0'

                        if 'REWARD IS' in line:
                            score = splitLine[splitLine.index('IS') + 1].strip()
                        elif 'REWARD' in line:
                            score = splitLine[splitLine.index('REWARD') + 1].strip()
                        else:
                            score = splitLine[splitLine.index('score') + 1].strip()

                        if 'LENGTH' in line:
                            actions = splitLine[splitLine.index('LENGTH') + 1].strip()
                        elif 'ACTION' in line:
                            actions = splitLine[splitLine.index('ACTION') + 1].strip()
                        else:
                            actions = splitLine[splitLine.index('action') + 1].strip()
                    row = [game_name, exp, it, mode, completed, score, actions]
                    writer.writerow(row)


