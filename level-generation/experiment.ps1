echo "Random Control"
python .\randomAgent.py .\games\training\human .\logs\Experiment2\Control > .\logs\Experiment2\randomControl.txt
echo "MCTS Control"
python .\mcts.py .\games\training\human .\logs\Experiment2\Control > .\logs\Experiment2\mctsControl.txt

echo "Random 1"
python .\randomAgent.py .\games\output\Experiment2\1 .\logs\Experiment2\1 > .\logs\Experiment2\random1.txt
echo "MCTS 1"
python .\mcts.py .\games\output\Experiment2\1 .\logs\Experiment2\1 > .\logs\Experiment2\mcts1.txt

echo "Random 2"
python .\randomAgent.py .\games\output\Experiment2\2 .\logs\Experiment2\2 > .\logs\Experiment2\random2.txt
echo "MCTS 2"
python .\mcts.py .\games\output\Experiment2\2 .\logs\Experiment2\2 > .\logs\Experiment2\mcts2.txt

echo "Random 3"
python .\randomAgent.py .\games\output\Experiment2\3 .\logs\Experiment2\3 > .\logs\Experiment2\random3.txt
echo "MCTS 3"
python .\mcts.py .\games\output\Experiment2\3 .\logs\Experiment2\3 > .\logs\Experiment2\mcts3.txt

echo "Random 4"
python .\randomAgent.py .\games\output\Experiment2\4 .\logs\Experiment2\4 > .\logs\Experiment2\random4.txt
echo "MCTS 4"
python .\mcts.py .\games\output\Experiment2\4 .\logs\Experiment2\4 > .\logs\Experiment2\mcts4.txt

echo "Random 5"
python .\randomAgent.py .\games\output\Experiment2\5 .\logs\Experiment2\5 > .\logs\Experiment2\random5.txt
echo "MCTS 5"
python .\mcts.py .\games\output\Experiment2\5 .\logs\Experiment2\5 > .\logs\Experiment2\mcts5.txt